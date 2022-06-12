import requests
import json
import os.path

from fasp.loc import DRSClient
#from fasp.examples.discoverySearch.getFirstModel import result


class Gen3DRSClient(DRSClient):
    '''Handles Gen3 specific authentication using Fence'''
    
    # Initialize a DRS Client for the service at the specified url base
    # and with the REST resource to provide an access key 
    def __init__(self, api_url_base,  access_token_resource_path, api_key_path,
    access_id=None, debug=False):
        super().__init__(api_url_base, access_id, debug=debug)
        self.access_token_resource_path = access_token_resource_path
        full_key_path = os.path.expanduser(api_key_path)
        with open(full_key_path) as f:
            self.api_key = json.load(f)
        code = self.updateAccessToken()
        if code == 401:
            print('Invalid access token in {}'.format(full_key_path))
        elif code != 200:
            print('Error {} getting Access token for {}'.format(code, api_url_base))
            print('Using {}'.format(full_key_path))


    # Obtain an access_token using the provided Fence API key.
    # The client object will retain the access key for subsequent calls
    def updateAccessToken(self):
        headers = {'Content-Type': 'application/json'}
        api_url = '{0}{1}'.format(self.api_url_base, self.access_token_resource_path)
        response = requests.post(api_url, headers=headers, json=self.api_key)

        if response.status_code == 200:
            resp = json.loads(response.content.decode('utf-8'))
            self.access_token = resp['access_token']
        return response.status_code
        


class crdcDRSClient(Gen3DRSClient):
    
    # Mostly done by the Gen3DRSClient, this just deals with url and end point specifics
    def __init__(self, api_key_path=None,  access_id=None,  debug=False):
        if api_key_path == None:
            api_key_path='~/.keys/crdc_credentials.json'
        super().__init__('https://nci-crdc.datacommons.io', '/user/credentials/api/access_token',
            api_key_path, access_id, debug)
        
        
class bdcDRSClient(Gen3DRSClient):
    
    # Mostly done by the Gen3DRSClient, this just deals with url and end point specifics
    def __init__(self, api_key_path, access_id=None,  debug=False):
        super().__init__('https://gen3.biodatacatalyst.nhlbi.nih.gov', '/user/credentials/cdis/access_token',
            api_key_path, access_id, debug)

class kfDRSClient(Gen3DRSClient):
    
    # Mostly done by the Gen3DRSClient, this just deals with url and end point specifics
    def __init__(self, api_key_path, access_id=None,  debug=False):
        super().__init__('https://data.kidsfirstdrc.org', '/user/credentials/cdis/access_token',
            api_key_path, access_id, debug)

class anvilDRSClient(Gen3DRSClient):
    
    
    def __init__(self, api_key_path, userProject=None, access_id=None,  debug=False):
        self.userProject = userProject
        super().__init__('https://gen3.theanvil.io','/user/credentials/api/access_token', api_key_path, access_id, debug)

    # Get a URL for fetching bytes. 
    # Anvil GCP resources requires you to provide the userAccount to which charges will be accrued
    # That user account must grant serviceusage.services.use access to your anvil service account
    # e.g. to user-123@anvilprod.iam.gserviceaccount.com
    def getAccessURL(self, object_id, access_id=None):
        result = super().getAccessURL(object_id, access_id)

        if result != None:
            if self.userProject == None:
                return result
            else:
                return '{}&userProject={}'.format(result, self.userProject)
        else:
            return None

if __name__ == "__main__":
    
    test_data = {'BioDataCatalyst' : {'drs_client': bdcDRSClient('~/.keys/bdc_credentials.json', 'gs', debug=True),
								'drs_ids': ['dbd55e76-1100-40b3-b420-0eaeee478fbc']
								},
				'Cancer Research Data Commons': {'drs_client': crdcDRSClient('~/.keys/crdc_credentials.json','s3'),
								'drs_ids': ['0e3c5237-6933-4d30-83f8-6ab721096bc7']}
		
		}
    
    for (testname, test) in test_data.items():
        print ('______________________________________')
        print (testname)
        drsClient = test['drs_client']
        for drs_id in test['drs_ids']:
            res = drsClient.getObject(drs_id)
            print(f'GetObject for {drs_id}')
            print (json.dumps(res,indent=3))
            print(f'URL for {drs_id}')
            url = drsClient.getAccessURL(drs_id)
            print (url)

           
