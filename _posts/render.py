
import argparse
import requests
import simplejson

def gitHubPost(text, mode, context):
    # Send a POST request to GitHub via API
	payload = {'text': text, 'mode':mode}
	if context != None:
		payload['context'] = context

	headers = {	'Accept': 'application/vnd.github+json',
				'Authorization': 'Bearer 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',
				'X-GitHub-Api-Version': '2022-11-28' }

	r = requests.post('https://api.github.com/markdown', data=simplejson.dumps(payload), headers=headers)

	if r.status_code == 200:
		return r.content
	else:
		# details = ''
		# for e in res['errors']:
		#	details += '{}.{}: {}.'.format(e['resource'], e['field'], e['code'])
		# print('[ERROR][HTTP {}] {} - {}'.format(r.status_code, res['message'], details))
		print('[ERROR][HTTP {}]'.format(r.status_code))
		return None


'''
    Get commandline arguments
'''
parser = argparse.ArgumentParser()
parser.add_argument('file',         help='input file name', type=str)
parser.add_argument('-m', '--mode', help='markdown rendering mode. Use markdown for readme file and gfm for comments, issues, etc.', choices=['markdown', 'gfm'], dest='mode', default='markdown')
parser.add_argument('-c', '--context', help='repository context when rendering in gfm mode', nargs=1, dest='context', type=str)
parser.add_argument('-o', '--output', help='output file name', nargs=1, dest='output', type=str)
args = parser.parse_args()

ifile = open(args.file, 'r')
try:
	md = ifile.read()
	ifile.close()
	html = gitHubPost(md, args.mode, args.context)
	html = html.decode('utf-8')
	if args.context != None and args.mode == 'markdown':
		print('[ERROR] Can not apply context in {} mode. Remove context or switch to gfm mode.'.format(args.mode))
	else:
		if args.output != None:
			ofile = open(args.output[0], 'w')
			ofile.write(html)
			ofile.close()
		else:
			print(html)

except IOError as e:
	print('[ERROR][I/O Exception] Error# {0}: {}'.format(e.errno, e.strerror))