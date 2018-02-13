import globus_sdk

from configparser import ConfigParser

parser = ConfigParser()
parser.read('../../etl_config.ini')

def _first(endpoints):
    for entry in endpoints:
        return entry

root_dir = parser.get("terraref","root_directory")
working_dirs = [x.strip() for x in parser.get("terraref","directories").split(",")]
dates = [x.strip() for x in parser.get("terraref","dates").split(",")]

client = globus_sdk.NativeAppAuthClient(parser.get('globus', 'client_id'))
client.oauth2_start_flow(refresh_tokens=True)

authorize_url = client.oauth2_get_authorize_url()
print('Please go to this URL and login: {0}'.format(authorize_url))

auth_code = input(
    'Please enter the code you get after login here: ').strip()
token_response = client.oauth2_exchange_code_for_tokens(auth_code)

# the useful values that you want at the end of this
globus_auth_data = token_response.by_resource_server['auth.globus.org']
globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']
globus_auth_token = globus_auth_data['access_token']
globus_transfer_token = globus_transfer_data['access_token']

# a GlobusAuthorizer is an auxiliary object we use to wrap the token. In
# more advanced scenarios, other types of GlobusAuthorizers give us
# expressive power
authorizer = globus_sdk.AccessTokenAuthorizer(globus_transfer_token)
tc = globus_sdk.TransferClient(authorizer=authorizer)

terraref = tc.get_endpoint(parser.get("globus", "terraref_endpoint"))
workbench = tc.get_endpoint(parser.get("globus", "workbench_endpoint"))

print("Terraref Endpoint name:",
      terraref["display_name"] or terraref["canonical_name"])

for dir in working_dirs:
    for date in dates:
        dir_to_transfer = "/".join([root_dir, dir, date])
        print(dir_to_transfer)

        tdata = globus_sdk.TransferData(tc, source_endpoint=terraref["id"],
                                        destination_endpoint=workbench["id"],
                                        label="DataDrivenAg",
                                        sync_level="checksum")
        tdata.add_item(dir_to_transfer+"/", "/~/data/datadrivenag/"+dir+"/"+date+"/", recursive=True)
        transfer_result = tc.submit_transfer(tdata)
        print("task_id =", transfer_result["task_id"])



# my_endpoint = _first(tc.endpoint_search('Docker', filter_scope='my-endpoints'))
# print(my_endpoint)
#
# tdata = globus_sdk.TransferData(tc, "ddb59af0-6d04-11e5-ba46-22000b92c6ec",
#                                 my_endpoint["id"],
#                                 label="SDK example",
#                                 sync_level="checksum")
#
# tdata.add_item("/share/godata/file2.txt", "/~/file2.txt.1")
# transfer_result = tc.submit_transfer(tdata)
# print("task_id =", transfer_result["task_id"])
