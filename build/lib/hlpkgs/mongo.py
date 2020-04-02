#!/usr/bin/env python

import functools
import inspect
import logging
from datetime import datetime
from pymongo.errors import PyMongoError
from pymongo.database import Database
from pymongo import MongoClient


class CatchMongoError:
    def __init__(self, error_type, default=None):
        self._default = default
        self._error_type = error_type

    def __call__(self, api, *args, **kwargs):
        wrapper = api
        if inspect.iscoroutinefunction(api):
            @functools.wraps(api)
            async def async_decorator(*args, **kwargs):
                try:
                    return await api(*args, **kwargs)
                except self._error_type as e:
                    logging.error(e)
                    return self._default
            wrapper = async_decorator
        else:
            @functools.wraps(api)
            def sync_decorator(*args, **kwargs):
                try:
                    return api(*args, **kwargs)
                except self._error_type as e:
                    logging.error(e)
                    return self._default
            wrapper = sync_decorator
        return wrapper


class CollectionWrapper:
    @classmethod
    def ValidFilters(cls, src: dict, keys: (list,tuple), **kwargs):
        retval = {}
        for key, value in src.items():
            if key not in keys:
                continue            
            retval.update({key: value})
        for defkey, defval in kwargs.items():
            if defkey not in keys:
                continue
            value = src.get(defkey, {})
            if isinstance(value, dict) and isinstance(defval, dict):
                defval.update(value)
            if defval:
                retval.update({defkey: defval})
        return retval

    @classmethod
    def SetCreationTime(cls, doc):
        if (not isinstance(doc, dict)):
            return
        now = datetime.now()
        doc.update({'creation_time': now, 'last_modified_time': now})

    @classmethod
    def UpdateLastModifiedTime(cls, doc):
        if (not isinstance(doc, dict)):
            return
        now = datetime.now()
        doc.update({'last_modified_time': now})

    def __init__(self, db :Database, name :str, **kwargs):
        try:
            self._instance = db.get_collection(name)
        except PyMongoError as e:
            self._instance = None
            PrintException()

    @CatchMongoError(PyMongoError, default=False)
    def InsertOne(self, doc, **kwargs):
        if not self._instance:
            return False
        self.SetCreationTime(doc)
        filters = self.ValidFilters(kwargs, ['bypass_document_validation', 'session'])
        logger.debug(doc)
        self._instance.insert_one(doc, **filters)
        return True

    @CatchMongoError(PyMongoError, default=False)
    def InsertMany(self, docs:list, **kwargs):
        if not self._instance:
            return False
        filters = self.ValidFilters(kwargs, ['bypass_document_validation', 'session'])
        self._instance.insert_many(docs, **filters)
        return True
            
    @CatchMongoError(PyMongoError, default={})
    def FindOne(self, qkeys, **kwargs):
        if not self._instance:
            return {}
        filters = self.ValidFilters(kwargs, ['projection'], projection={'_id': 0})
        result = self._instance.find_one(qkeys, **filters)       
        return result

    @CatchMongoError(PyMongoError, default=[])
    def Find(self, qkeys, **kwargs):
        if not self._instance:
            return []
        filters = self.ValidFilters(kwargs, ['projection'], projection={'_id': 0})
        result = self._instance.find(qkeys, **filters)       
        return [r for r in result]

    @CatchMongoError(PyMongoError, default={})
    def UpdateOne(self, qkeys, doc, **kwargs):
        if not self._instance:
            return {}
        self.UpdateLastModifiedTime(doc)
        filters = self.ValidFilters(kwargs, ['projection', 'sort', 'upsert', 'return_document', 'session'], projection={'_id': 0})
        result = self._instance.find_one_and_update(qkeys, {'$set': doc}, **filters)
        return result

    @CatchMongoError(PyMongoError, default=0)
    def DeleteOne(self, qkeys, **kwargs):
        if not self._instance:
            return 0
        filters = self.ValidFilters(kwargs, ['collation', 'session'])
        result = self._instance.delete_one(qkeys, **filters)
        return result.deleted_count

    @CatchMongoError(PyMongoError, default=0)
    def DeleteMany(self, qkeys, **kwargs):
        if not self._instance:
            return 0
        filters = self.ValidFilters(kwargs, ['collation', 'session'])
        result = self._instance.delete_many(qkeys, **filters)
        return result.deleted_count


    @CatchMongoError(PyMongoError, default={})
    def Aggregate(self, pipeline, **kwargs):
        if not self._instance:
            return {}
        filters = self.ValidFilters(kwargs, ['options'])
        result = self._instance.aggregate(pipeline, **kwargs)
        return [line for line in result]

    @CatchMongoError(PyMongoError, default={})
    def FindOneAndUpdate(self, qkeys, update, **kwargs):
        if not self._instance:
            return {}
        filters = self.ValidFilters(kwargs, ['projection', 'sort', 'upsert', 'return_document', 'session'], projection={'_id': 0})
        result = self._instance.find_one_and_update(qkeys, update, **filters)
        return result



__all__ = ['CollectionWrapper']


