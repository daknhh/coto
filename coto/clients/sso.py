import json
from bs4 import BeautifulSoup
from . import BaseClient
import os
region = os.getenv('AWS_DEFAULT_REGION')

print(f"🌎 Get region from env: AWS_DEFAULT_REGION - Region {region}")

class Client(BaseClient):
    """
    A low-level client representing Biling:

    .. code-block:: python

        import coto

        session = coto.Session()
        client = session.client('sso')

    These are the available methods:
    """
    def __init__(self, session):
        super().__init__(session)
        self.__xsrf_token = None

    def _url(self, api):
        return "https://"+ region+"console.aws.amazon.com/singlesignon/{0}".format(api)

    def _xsrf_token(self):
        if self.__xsrf_token is None:
            self._get_xsrf_token()
        return self.__xsrf_token 

    def _get_xsrf_token(self):
        r = self.session()._get(
            "https://"+ region+".console.aws.amazon.com/singlesignon/identity/home?region="+region+"&state=hashArgs%23")

        if r.status_code != 200:
            raise Exception("failed get token")

        soup = BeautifulSoup(r.text, 'html.parser')
        for m in soup.find_all('meta'):
            if 'name' in m.attrs and m['name'] == "awsc-csrf-token":
                self.__xsrf_token = m['content']
                print("🔑 Successfully obtain xsrf_token")
                return

        raise Exception('unable to obtain SSO xsrf_token')



    def _post(self,operation):
        apiendpoint = "https://" + region +".console.aws.amazon.com/singlesignon/api/peregrine"
        x_amz_target = "com.amazon.switchboard.service.SWBService."+operation
        headers={'x-csrf-token': self._xsrf_token(),
            "X-Amz-Target": x_amz_target,
            "Content-Encoding": "amz-1.0",
            "Accept": "application/json, text/javascript, */*",
            "Content-Type": "application/json"}
        json_body = {
            "headers": headers,
            "operation":operation,"contentString":"{}",
            "region":region,"path":"/control/"
        }
        r = self.session()._post(
            apiendpoint,
            data=json.dumps(json_body),
            headers={'x-csrf-token': self._xsrf_token(),
            "X-Amz-Target": x_amz_target,
            "Accept": "application/json, text/javascript, */*","content-type":"application/json"}
            )
        if r.status_code != 200:
            raise Exception("failed get")

        return r

    # sso api

    def list_associations(self):
        """
        Obtain the list of the sso associations.

        Status:

        Request Syntax:
            .. code-block:: python

                response = client.list_associations()

        Returns:
            string: status
        """
        operation = "ListDirectoryAssociations"
        r = self._post(operation)
        return json.loads(r.text)

