"""Default is offline dry-run; explicit --execute uploads privately to verified channel."""
import argparse
import json
import os
from pathlib import Path
from pipeline import digest


def plan(path):
    m = json.loads(path.read_text())
    video = (path.parent/m['video']).resolve()
    if video.parent != path.parent.resolve() or digest(video) != m['sha256']:
        raise ValueError('Video path/hash mismatch; regenerate package')
    if not m['title'].strip() or len(m['title']) > 100:
        raise ValueError('YouTube title must contain 1–100 characters')
    body = {'snippet': {'title': m['title'], 'description': m['description'],
                        'categoryId': m['youtube']['category_id'], 'defaultLanguage': m['language']},
            'status': {'privacyStatus': 'private',
                       'selfDeclaredMadeForKids': m['youtube']['made_for_kids']}}
    return m, video, body


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest', type=Path)
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    manifest = a.manifest.resolve()
    m, video, body = plan(manifest)
    if not a.execute:
        print(json.dumps({'mode': 'DRY_RUN', 'channel_id': m['youtube']['channel_id'],
                          'preview': m['preview'], 'body': body}, indent=2))
        return
    if m['preview'] or m['status'] != 'approved':
        p.error('Upload requires a final render with status=approved after review')
    channel = m['youtube']['channel_id']
    if not channel:
        p.error('Set the intended channel_id explicitly')
    receipt = manifest.parent/'upload-receipt.json'
    lock = manifest.parent/'upload-started.json'
    if receipt.exists() or lock.exists():
        p.error('Upload already recorded or started; inspect YouTube before retrying')
    # Never inspect or copy credentials from another project/channel.
    token = os.environ.get('YOUTUBE_TOKEN_FILE')
    if not token:
        p.error('Set YOUTUBE_TOKEN_FILE to an authorized OAuth token file')
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    creds = Credentials.from_authorized_user_file(token, ['https://www.googleapis.com/auth/youtube.upload',
                                                         'https://www.googleapis.com/auth/youtube.readonly'])
    if not creds.valid:
        if not creds.refresh_token:
            p.error('OAuth refresh token is missing')
        creds.refresh(Request())
    service = build('youtube', 'v3', credentials=creds, cache_discovery=False)
    channels = service.channels().list(part='id', mine=True).execute().get('items', [])
    if channel not in {item['id'] for item in channels}:
        p.error('OAuth identity does not match the intended channel')
    # Persistent marker prevents silent duplicate uploads after interrupted requests.
    with lock.open('x') as f:
        json.dump({'sha256': m['sha256'], 'channel_id': channel}, f)
    request = service.videos().insert(part='snippet,status', body=body,
               media_body=MediaFileUpload(str(video), mimetype='video/mp4', resumable=True))
    response = None
    while response is None:
        _, response = request.next_chunk()
    receipt.write_text(json.dumps({'id': response['id'], 'sha256': m['sha256'],
                                   'channel_id': channel, 'privacy': 'private'}, indent=2)+'\n')
    print('Private upload recorded:', response['id'])


if __name__ == '__main__':
    main()
