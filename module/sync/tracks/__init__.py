import pydash as _
from common.mongo import oplog_client
from common.elasticsearch.doc_manager import mongo_docman
from model import merchant, impression_track, act_share_detail

from ..sync_manager import SyncManager
from module.constant import mapping

from . import track_util

_map = mapping.tracks
_index = _map.get('index')
_types = _map.get('types')
_routing = _map.get('routing')
_mappings = _map.get('mappings')
_settings = _map.get('settings')

merchant_sync_manager = SyncManager(oplog_client,
                                    mongo_docman,
                                    collection=merchant,
                                    namespace=_types.get('merchant').get('namespace'),
                                    query_options={
                                        'projection': {'createTime': 0}
                                    })

impression_track_sync_manager = SyncManager(oplog_client,
                                            mongo_docman,
                                            collection=impression_track,
                                            namespace=_types.get('impression_track').get('namespace'))

act_share_detail_sync_manager = SyncManager(oplog_client,
                                            mongo_docman,
                                            collection=act_share_detail,
                                            namespace=_types.get('act_share_detail').get('namespace'))


def _it_doc_process(doc):
    doc = {**doc, **track_util.url_split(doc.get('uri'))}
    if doc.get('senderToUserId') and _.get(doc, 'params.sender'):
        doc['salesId'], doc['params']['sender'] = _.get(doc, 'params.sender'), doc['senderToUserId']
    if _.has(doc, 'params.secondlevel'):
        doc['_parent'] = _.get(doc, 'params.secondlevel')
    return doc


def create_index():
    if not mongo_docman.es_sync.indices.exists(_index):
        res = mongo_docman.es_sync.indices.create(index=_index, body={
            'mappings': _mappings,
            'settings': _settings
        })

        # todo: 处理结果


def index_all():
    merchant_sync_manager.index_all()
    impression_track_sync_manager.index_all(doc_process_func=_it_doc_process)
    act_share_detail_sync_manager.index_all(doc_process_func=_it_doc_process)


def real_time_sync():
    merchant_sync_manager.real_time_sync()
    impression_track_sync_manager.real_time_sync(ops=('i', 'd'), doc_process_funcs={'i': _it_doc_process})
    act_share_detail_sync_manager.real_time_sync(ops=('i', 'd'), doc_process_funcs={'i': _it_doc_process})
