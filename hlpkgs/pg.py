import asyncio
from datetime import datetime
import logging
from aiopg import create_pool as create_engine
from query_condition import QueryCondition

class EngineWrapper:
    def __init__(self, **kwargs):
        self.kwargs_ = kwargs
        self.engine_ = None

    def __bool__(self):
        return True if self.engine_ else False

    async def Create(self):
        try:
            self.engine_ = await create_engine(loop=asyncio.get_event_loop(), **self.kwargs_)
        except Exception as e:
            logging.error(e)

    async def Close(self):
        if self.engine_:
            try:
                self.engine_.close()
                await self.engine_.wait_closed()
            except Exception as e:
                logging.error(e)

    async def __aenter__(self):
        await self.Create()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.Close()

    async def GetConnection(self):
        conn = None
        if self.engine_:
            try:
                conn = await self.engine_.acquire()
            except Exception as e:
                logging.error(e)
        return conn

    async def ReleaseConnection(self, conn):
        if conn and self.engine_:
            try:
                self.engine_.release(conn)
            except Exception as e:
                logging.error(e)

    def __bool__(self):
        return True if self.engine_ else False

class ConnWrapper:
    def __init__(self, engine: EngineWrapper):
        self.engine_ = engine

    async def Create(self):
        self.conn_ = await self.engine_.GetConnection()

    async def Close(self):
        await self.engine_.ReleaseConnection(self.conn_)

    async def __aenter__(self):
        await self.Create()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.Close()

    async def Execute(self, sql, args):
        if self.conn_:
            try:
                async with self.conn_.cursor() as cur:
                    return await cur.execute(sql, args)
            except Exception as e:
                logging.error('sql: {}'.format(sql))
                logging.error('args: {}'.format(args))
                logging.error(e)
        return None

    async def Commit(self):
        if self.conn_:
            return await self.conn_.commit()
        return None

    async def Query(self, sql, args):
        if self.conn_:
            try:
                async with self.conn_.cursor() as cur:
                    await cur.execute(sql, args)
                    result = await cur.fetchall()
                    return result
            except Exception as e:
                logging.error('sql: {}'.format(sql))
                logging.error('args: {}'.format(args))
                logging.error(e)
        return []

class SqlWrapper:
    def __init__(self, sql, *args):
        self.sql_ = sql
        self.args_ = args
    
    async def Execute(self, conn: ConnWrapper):
        result =  await conn.Execute(self.sql_, self.args_)
        return result

    async def Query(self, conn: ConnWrapper, limit: int = None, offset: int = None, page_index: int = None, page_size: int = None):
        if limit:
            self.sql_ = '{} limit {}'.format(self.sql_, limit)
            if offset:
                self.sql_ = '{} offset {}'.format(self.sql_, offset)
        elif page_size:
            self.sql_ = '{} limit {}'.format(self.sql_, page_size)
            if page_index:
                self.sql_ = '{} offset {}'.format(self.sql_, page_index*page_size)
        result = await conn.Query(self.sql_, self.args_)
        return result


class TableWrapper:
    def __init__(self, tablename):
        self.tablename_ = tablename
    
    async def Query(self, conn: ConnWrapper, keys: QueryCondition, *fields, orderkeys: str = None, limit: int = None, offset: int = None, page_index: int = None, page_size: int = None):
        sql = ''
        if keys:
            sql = 'select {fields} from {tablename} where {keys}'.format(fields=','.join(fields), tablename=self.tablename_, keys=keys.str())
        else:
            sql = 'select {fields} from {tablename}'.format(fields=','.join(fields), tablename=self.tablename_)
        groupby = keys.groupby()
        if groupby:
            sql = '{} {}'.format(sql, groupby)
        if orderkeys:
            sql = '{} order by {}'.format(sql, orderkeys)
        if limit:
            sql = '{} limit {}'.format(sql, limit)
            if offset:
                sql = '{} offset {}'.format(sql, offset)
        elif page_size:
            sql = '{} limit {}'.format(sql, page_size)
            if page_index:
                sql = '{} offset {}'.format(sql, page_index*page_size)
        if keys:
            return await conn.Query(sql, tuple(keys.Values()))
        else:
            return await conn.Query(sql, None)

    async def Insert(self, conn: ConnWrapper, **kwargs):
        fields, values = [], []
        for key in kwargs:
            if kwargs[key]:
                fields.append(key)
                values.append(kwargs[key])
        if not fields:
            return None
        sql = 'insert into {tablename} ({fields}) values ({values})'.format(tablename=self.tablename_, fields=','.join(fields), values=','.join(['%s']*len(values)))
        result = await conn.Execute(sql, tuple(values))
        return result

    async def InsertIfNotExist(self, conn: ConnWrapper, unique_keys: tuple, **kwargs):
        fields, values = [], []
        keys = QueryCondition()
        for key in kwargs:
            if kwargs[key]:
                fields.append(key)
                values.append(kwargs[key])
            if key in unique_keys:
                keys.EQ(key, kwargs[key])
        if not fields:
            return None
        sql = 'insert into {tablename} ({fields}) values ({values}) on conflict ({ukeys}) do nothing'.format(
            tablename=self.tablename_, fields=','.join(fields), values=','.join(['%s']*len(values)),
            ukeys=','.join(unique_keys)
            )
        result = await conn.Execute(sql, tuple(values+keys.Values()))
        return result

    async def InsertUpdate(self, conn: ConnWrapper, unique_keys: tuple, **kwargs):
        fields, values, update_fields, update_values = [], [], [], []
        for key in kwargs:
            if kwargs[key]:
                fields.append(key)
                values.append(kwargs[key])
                if key not in unique_keys:
                    update_fields.append(key)
                    update_values.append(kwargs[key])
        if not fields:
            return None
        sql = ''
        result = None
        if update_fields:
            sql = 'insert into {tablename} ({fields}) values ({values}) on conflict do update set {setkeys}'.format(
                tablename=self.tablename_, fields=','.join(fields), values=','.join(['%s']*len(values)),
                setkeys=','.join(['{}=%s'.format(field) for field in update_fields])
                )
            result = await conn.Execute(sql, tuple(values)+tuple(update_values))
        else:
            result = await self.InsertIfNotExist(conn, unique_keys, **kwargs)
        return result

    async def Update(self, conn: ConnWrapper, keys: QueryCondition, **kwargs):
        fields, values = [], []
        for key in kwargs:
            if kwargs[key]:
                fields.append(key)
                values.append(kwargs[key])
        if not fields:
            return None
        if keys:
            sql = 'update {tablename} set {fields} where {keys}'.format(tablename=self.tablename_, fields=','.join(['{}=%s'.format(key) for key in fields]), keys=keys.str())
            result = await conn.Execute(sql, tuple(values)+tuple(keys.Values()))
            return result
        else:
            sql = 'update {tablename} set {fields}'.format(tablename=self.tablename_, fields=','.join(['{}=%s'.format(key) for key in fields]))
            result = await conn.Execute(sql)
            return result


__all__ = ['EngineWrapper', 'ConnWrapper', 'SqlWrapper', 'TableWrapper']


