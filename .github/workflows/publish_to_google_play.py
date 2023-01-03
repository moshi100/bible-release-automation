import argparse
from googleapiclient.discovery import build
import httplib2
import os
from oauth2client import client

import mimetypes
mimetypes.add_type('application/octet-stream', '.aab')

TRACK = 'production'  # Can be 'alpha', beta', 'production' or 'rollout'
SERVICE_ACCOUNT_EMAIL = (
    'ENTER_YOUR_SERVICE_ACCOUNT_EMAIL_HERE@developer.gserviceaccount.com')

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('package_name',
                       help='The package name. Example: com.android.sample')
argparser.add_argument('file',
                       nargs='?',
                       default='app.aab',
                       help='The path to the file to upload.')


def main():
  # Load the key in PKCS 12 format that you downloaded from the Google APIs
  # Console when you created your Service account.
  # f = file('key.p12', 'rb')
  # key = f.read()
  key = os.getenv('SERVICE_ACCOUNT')
 # f.close()

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with the Credentials. Note that the first parameter, service_account_name,
  # is the Email address created for the Service account. It must be the email
  # address associated with the key that was created.
  credentials = client.SignedJwtAssertionCredentials(
      SERVICE_ACCOUNT_EMAIL,
      key,
      scope='https://www.googleapis.com/auth/androidpublisher')
  http = httplib2.Http()
  http = credentials.authorize(http)

  service = build('androidpublisher', 'v2', http=http)

  # Process flags and read their values.
  flags = argparser.parse_args()

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
        body={u'versionCodes': [apk_response['versionCode']]}).execute()

    print( 'Track %s is set for version code(s) %s' % (
        track_response['track'], str(track_response['versionCodes'])))

    commit_request = service.edits().commit(
        editId=edit_id, packageName=package_name).execute()

    print ('Edit "%s" has been committed' % (commit_request['id']))

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main()