import argparse
import sys
import os

from googleapiclient.discovery import build
from google.oauth2 import service_account


import mimetypes
mimetypes.add_type('application/octet-stream', '.aab')

TRACK = 'production'  # Can be 'alpha', beta', 'production' or 'rollout'
SERVICE_ACCOUNT_EMAIL = (
    'google-play-publisher@api-7797719130150548635-666544.iam.gserviceaccount.com')

SERVICE_ACCOUNT_KEY = os.getenv('SERVICE_ACCOUNT_ANDROID') 
SERVICE_ACCOUNT_FILE = 'gcp_service_account.json'

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('package_name',
                       help='The package name. Example: com.android.sample')
argparser.add_argument('file',
                       nargs='?',
                       default='app.aab',
                       help='The path to the file to upload.')


def main(argv):
  # Authenticate and construct service.
  '''
  credentials = client.SignedJwtAssertionCredentials(
      SERVICE_ACCOUNT_EMAIL,
      SERVICE_ACCOUNT_KEY,
      scope='https://www.googleapis.com/auth/androidpublisher')

  '''


  SCOPES = ['https://www.googleapis.com/auth/androidpublisher']

  credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

  http = httplib2.Http()
  http = credentials.authorize(http)
  service = build('androidpublisher', 'v2', http=http)


  # Process flags and read their values.
  flags = argparser.parse_args()

  # Process flags and read their values.
  package_name = flags.package_name
  apk_file = flags.apk_file

  try:
    edit_request = service.edits().insert(body={}, packageName=package_name)
    result = edit_request.execute()
    edit_id = result['id']

    apk_response = service.edits().apks().upload(
        editId=edit_id,
        packageName=package_name,
        media_body=apk_file).execute()

    print ('Version code %d has been uploaded' % apk_response['versionCode'])

    track_response = service.edits().tracks().update(
        editId=edit_id,
        track=TRACK,
        packageName=package_name,
        body={u'releases': [{
            u'name': u'My first API release with release notes',
            u'versionCodes': [str([apk_response['versionCode']])],
            u'releaseNotes': [
                {u'recentChanges': u'Apk recent changes in en-US'},
            ],
            u'status': u'completed',
        }]}).execute()

    print ('Track %s is set with releases: %s' % (
        track_response['track'], str(track_response['releases'])))

    commit_request = service.edits().commit(
        editId=edit_id, packageName=package_name).execute()

    print ('Edit "%s" has been committed' % (commit_request['id']))

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)