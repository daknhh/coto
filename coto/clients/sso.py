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
        print(f"⚙️  Init SSO Client")
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



    def _post(self,operation,contentstring):
        apiendpoint = "https://" + region +".console.aws.amazon.com/singlesignon/api/peregrine"
        x_amz_target = "com.amazon.switchboard.service.SWBService."+operation
        headers={'x-csrf-token': self._xsrf_token(),
            "X-Amz-Target": x_amz_target,
            "Content-Encoding": "amz-1.0",
            "Accept": "application/json, text/javascript, */*",
            "Content-Type": "application/json"}

        json_body = {
            "headers": headers,
            "operation":operation,"contentString": f"{json.dumps(contentstring)}",
            "region":region,"path":"/control/"
        }
        r = self.session()._post(
            apiendpoint,
            data=json.dumps(json_body),
            headers={'x-csrf-token': self._xsrf_token(),
            "X-Amz-Target": x_amz_target,
            "Accept": "application/json, text/javascript, */*","content-type":"application/json"}
            )
        if r.status_code == 200:
            print(f"✅ Successfully invoked: {operation}")
        if r.status_code != 200:
            raise Exception("failed post")

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
        contentstring = {}
        r = self._post(operation,contentstring)
        return json.loads(r.text)

    def disassociate_directory(self,directoryId,directoryType):
        """
        Associate Directory to the sso.

        Status:

        Request Syntax:
            .. code-block:: python

                response = client.disassociate_directory(
                    directoryId, #Id of the directory
                    directoryType #eg. ADConnector
                )

        Returns:
            string: status
        """
        operation = "DisassociateDirectory"
        contentstring = {"directoryId":directoryId,"directoryType":directoryType}
        r = self._post(operation,contentstring)
        return json.loads(r.text)


    def associate_directory(self,directoryId,directoryType):
        """
        Associate Directory to the sso.

        Status:

        Request Syntax:
            .. code-block:: python

                response = client.associate_directory(
                    directoryId, #Id of the directory
                    directoryType #eg. ADConnector
                )

        Returns:
            string: status
        """
        operation = "AssociateDirectory"
        contentstring = {"directoryId":directoryId,"directoryType":directoryType}
        r = self._post(operation,contentstring)
        return json.loads(r.text)
