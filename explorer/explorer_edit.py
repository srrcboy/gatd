#!/usr/bin/env python2

import json
import os
import sys

sys.path.append(os.path.abspath('../config'))
sys.path.append(os.path.abspath('../formatter'))
import MongoInterface

import edit_tree

def strip (d):
	if '' in d:
		del d['']

def confirm (prompt, default=False):
	default_chr = 'y' if default else 'n'

	while True:
		resp = raw_input('{} [{}]: '.format(prompt, default_chr)).strip().lower()

		# If nothing was entered then just return whatever is the default
		if not resp:
			return default

		if resp in ['y', 'ye', 'yes', 'true']:
			return True
		elif resp in ['n', 'no', 'false']:
			return False

		print('Bad response. Try again.')



def edit_meta (req_key, req_key_val, query, addit):
	while True:
		req_key_val, query, addit = edit_item.edit_meta(req_key,
		                                                req_key_val,
		                                                query,
		                                                addit)
		strip(query)
		strip(addit)
		print('\nMeta Record:')
		print(DSTR_A.format(req_key, 'QUERY', 'ADDITIONAL'))
		print(DSTR_A.format(req_key_val, query, addit))
		if not confirm('Continue editing?'):
			break
	return (req_key_val, query, addit)


def print_keys (indent, key_list):
	indent_str = ' '*indent

	if not key_list:
		return

	for k in key_list:
		print('{}{}'.format(indent_str, k['key']))
		print_keys(indent+4, k['children'])


def parseNewTree (lines, thislist, indent):

	i = 0
	while i < len(lines):

		line = lines[i]

		lineindent = 0
		for c in line:
			if c == ' ':
				lineindent += 1
			else:
				break

		if lineindent == indent:
			thislist.append({'key': line.strip(), 'children': []})
			i += 1

		elif lineindent > indent:
			i += parseNewTree(lines[i:], thislist[-1]['children'], lineindent)

		else:
			return i
	return i




DSTR_T = '[idx] {:<25s} {:<20s} {:<50s}'
DSTR   = '[{:>3d}] {:<25s} {:<20s} {:<50s}'

DSTR_A = '      {:<25s} {:<20s} {:<50s}'

pids = []



m = MongoInterface.MongoInterface()


# List all of the profiles so we can edit the key layout for the proper one
configs = m.getAllConfigs()

print('Choose which profile you want:')
for i, c in zip(range(len(configs)), configs):
	pids.append(c['profile_id'])
	print('[{:>3d}] {}'.format(i, c['parser_name']))
cidx = int(raw_input('Index: '))
print('')


explorekeysdb = m.getExploreKeysSingle(pids[cidx])

if not explorekeysdb:
	# Haven't set this one up yet
	# Do so now
	m.addExploreKeys(pids[cidx], json.dumps([]))
	explorekeysdb = m.getExploreKeysSingle(pids[cidx])



name = m.getConfigByProfileId(explorekeysdb['profile_id'])['parser_name']

print('Editing Explore keys for {}\n'.format(name))

explorekeys = json.loads(explorekeysdb['keys_json'])

# Loop until the user is happy with the result
while True:

	# Run the editor so we can update the explore key tree
	newtreetxt = edit_tree.edit_tree(explorekeys)

	# Convert text to list/dict structure
	explorekeys = []
	parseNewTree(newtreetxt.strip().split('\n'), explorekeys, 0)

	print('New Explore Key tree:\n')
	print_keys(0, explorekeys)
	print('')


	if not confirm('Continue editing?', False):
		break

m.updateExploreKeys(explorekeysdb['_id'],
                    explorekeysdb['profile_id'],
                    json.dumps(explorekeys))


print('Updated Explore Keys for {}'.format(name))

