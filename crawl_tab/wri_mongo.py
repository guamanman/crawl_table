# 2016.06.22 20:30:09 PDT
#Embedded file name: /home/zhangman-s/Documents/crawl_tab/wri_mongo.py
__author__ = 'zhangman-s'
import pymongo
import pymongo.collection
import pymongo.results
mongo_client = None
mongo_db = None
#MONGO_HOST = '220.181.156.245'
MONGO_HOST = '10.131.120.234'
MONGO_PORT = 27017
#MONGO_DB = 'shuaji'
MONGO_DB = 'vulnerability_database'



def connect():
    global mongo_db
    global mongo_client
    try:
        mongo_client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        mongo_db = mongo_client.get_database(MONGO_DB)
    except Exception as e:
        print "Can't connect to the mongo db"

    if mongo_client and mongo_db:
        return mongo_db
    else:
        print 'Connect to the mongo db failed.Please check the params.'
        return None


def get_con():
    if mongo_db:
        return mongo_db
    else:
        print "Can't connect to the mongo db when using. Reconnect it."
        connect()
        return mongo_db


def get_col(table_name):
    return pymongo.collection.Collection(get_con(), table_name)


def db_result_handle(result, method_log):
    if result is not None and result.acknowledged is True:
        return True
    elif result is None:
        log_util.print_error('exec %s failed,result is null' % method_log)
        return False
    elif isinstance(result, pymongo.results.InsertManyResult) and result.inserted_ids is not None:
        log_util.print_error('exec %s failed,len(result.inserted_ids)=%s' % (method_log, len(result.inserted_ids)))
        return False
    elif isinstance(result, pymongo.results.UpdateResult) and result.inserted_ids is not None:
        log_util.print_error('exec %s failed,result.matched_count=%s,result.modified_count=%s' % (method_log, result.matched_count, result.modified_count))
        return False
    elif isinstance(result, pymongo.results.DeleteResult) and result.inserted_ids is not None:
        log_util.print_error('exec %s failed,result.deleted_count=%s' % (method_log, len(result.deleted_count)))
        return False
    else:
        log_util.print_error('exec %s failed,result=%s' % (method_log, str(result)))
        return False


def insert_table(apk_doc):
    method_log = 'db_op_apk_mongo.insert_table(apk_doc=%s)' % str(apk_doc)
    try:
        white_col = get_col('vulnerability_test')
        cur = white_col.find({'id': apk_doc['id']})
        if not cur or cur.count() == 0:
            result = white_col.insert_one(apk_doc)
            return db_result_handle(result, method_log)
    except Exception as e:
        print '%s got exception ' % method_log
        print e
        return False


def Add_item(id, new):
    method_log = 'db_op_apk_mongo.insert_item(id=%s)' % str(id)

    try:
        white_col = get_col('vulnerability_test')
        ori = white_col.find({'id': str(id)})
        if ori and ori.count() != 0:
            for ori_item in ori:
                for key, value in new.items():

                        ori_item[str(key)].append(value)

            result = white_col.update({'id': str(id)}, {'$set': ori_item})

            # return db_result_handle(result, method_log)
    except Exception as e:
        print '%s got exception ' % method_log
        print e
        raise
        return False

