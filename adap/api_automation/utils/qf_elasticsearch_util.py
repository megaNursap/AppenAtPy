from elasticsearch import Elasticsearch
import logging

from adap.api_automation.utils.data_util import decrypt_message


LOGGER = logging.getLogger(__name__)

elasticsearch_url = {
    'integration': 'gAAAAABjybk6wrnqQ8kPcZzNG6MA81QonoQe3d8rOpnfXrBFpvCriF87G20zrkdlsM5Y6alOy1R8Sx0Ma9QjQ-hj6cd5EXXSaGu10MbOuc1gKbss1BoBLGmlpxRzJ219SaBo6ibE5dy1cZhE_nnsmSByPgsSv5X5ZSaOjGUIPmwG3UWSLRF5HE6F_RnUeT4R5bkRFtHk2QuC',
    'sandbox': '',
    'staging': ''
}

white_list = {
    'integration': [
        "c87f67ec-8618-4644-8ab8-8f97d8073c94",
        "6bbdfa50-d71e-4ab7-8237-3b750942a22d",
        "cf96b4a8-8926-476f-8194-9b2ca71408ef",
        "b76c15a9-e412-45d8-8d2e-da31d532525e",
        "2283a48e-5b80-4669-9957-76ed4a810caa"
    ],
    'sandbox': [],
    'staging': []
}


class ElasticsearchQF:
    supported_index_type = ['project', 'unit-metrics', 'unit-breakdown']

    def __init__(self, env):
        self.url = decrypt_message(elasticsearch_url[env])
        self.es = Elasticsearch([self.url])

    def delete_index_for_project(self, index_type, project_id):
        if project_id in white_list:
            LOGGER.info(f'[{project_id}] is in white_list, no need to clean up the index')
        elif index_type not in self.supported_index_type:
            LOGGER.info(f'[{index_type}] is not supported type, we only support the index_type: {self.supported_index_type}')
        else:
            index = f'{index_type}-{project_id}'
            ## If index exists, then delete it
            if self.es.indices.exists(index=index):
                try:
                    resp = self.es.indices.delete(index=index)
                    LOGGER.info(resp)
                    LOGGER.info(f'Deleted index [{index}] success')
                except Exception as e:
                    LOGGER.error(e)
            else:
                LOGGER.info(f'Index = [{index}] not exists, no need to delete it')

    def delete_all_index(self, project_id):
        LOGGER.info(f"Preparing delete all index for {project_id}")
        for index_type in self.supported_index_type:
            self.delete_index_for_project(index_type, project_id)

    def delete_indexes_for_projects(self, project_list):
        LOGGER.info(f" Delete indexes for projects {project_list}")
        for project_id in project_list:
            self.delete_all_index(project_id)

