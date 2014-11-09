# PRESIDENTS = set([
# 				'George_Washington', 'John_Adams', 'Thomas_Jefferson',
# 				'James_Madison', 'James_Monroe','John_Quincy_Adams',
# 				'Andrew_Jackson','Martin_Van_Buren', 'William_Henry_Harrison',
# 				'John_Tyler', 'James_K._Polk', 'Zachary_Taylor',
# 				'Millard_Fillmore', 'Franklin_Pierce', 'James_Buchanan',
# 				'Abraham_Lincoln', 'Andrew_Johnson', 'Ulysses_S._Grant',
# 				'Rutherford_B._Hayes', 'James_A._Garfield', 'Chester_A._Arthur',
# 				'Grover_Cleveland', 'Benjamin_Harrison', 'William_McKinley',
# 				'Theodore_Roosevelt', 'William_Howard_Taft', 'Woodrow_Wilson', 
# 				'Warren_G._Harding', 'Calvin_Coolidge', 'Herbert_Hoover', 
# 				'Franklin_D._Roosevelt', 'Harry_S._Truman',
# 				'Dwight_D._Eisenhower', 'John_F._Kennedy', 'Lyndon_B._Johnson',
# 				'Richard_Nixon', 'Gerald_Ford', 'Jimmy_Carter', 'Ronald_Reagan',
# 				'George_H._W._Bush', 'Bill_Clinton', 'George_W._Bush',
# 				'Barack_Obama'
# ])

def redirects_set():

	print "Creating set of redirect pages..."
	redirects = set()

	with open('redirects_en.ttl', 'r') as r:
		for line in r:
			l = line.split()
			start = l[0][29:-1]
			redirects.add(start)

	return redirects # as a set

def names_dict():

	print "Creating dictionary of names..."
	names = {}

	with open('labels_en.ttl', 'r') as r:
		for line in r:
			l = line.partition('<http://www.w3.org/2000/01/rdf-schema#label>')
			name_link = l[0][29:-2]
			name = l[2][1:-3].replace('@en', '').replace('"', '')
			names[name_link] = name

	return names # as a dict

def types_dict():

	print "Creating dictionary of types..."
	types = {}

	with open('instance_types_en.ttl', 'r') as r:
		for line in r:
			l = line.split()
			if l[2][:29] == '<http://dbpedia.org/ontology/': # only if the type is dbpedia's
				name_link = l[0][29:-1]
				typ = l[2][29:-1]
				if '__' in name_link:
					continue
				if name_link in types: # are you currently in a topic?
					continue
					# types[name_link].append(typ) # use this to append all types
				else:
					types[name_link] = typ
					# types[name_link] = [typ] # for collecting more than one type

	return types # as a dict

def parse_links():

	redirects = redirects_set() # create set of redirects
	names = names_dict()
	types = types_dict()

	topics = {}
	data = {}
	
	counter = 50000000
	id_counter = 0

	print "Writing 'rels.csv'..."

	with open('page_links_en.ttl', 'r') as f, open('rels.csv', 'wb+') as c:
		c.write('start\tend\ttype\n') # write headers
		f.next()

		for line in f:
			if counter > 0:

				if counter % 100000 == 0:
					print "counter:", counter

				l = line.split()
				start = l[0][29:-1]
				end = l[2][29:-1]

				if start in topics: # are you currently in a topic?
					if end in topics[start]: # are you a repeat link?
						continue
					else:
						topics[start].append(end) # add yourself to topics
				else:
					topics = { start: [end] } # overwrite topics dict with new topic

				if start not in redirects and end[:5] != "File:":

					if start not in data: # are you a new node?
						
						data[start] = { 'id':   id_counter, 
										'name': names.get(start, start) }
						if types.get(start, 0) != 0: # only add type if it is known
							data[start].update({'type': types[start]})
						id_counter += 1

					if end not in data: # are you a new node?

						data[end] = { 'id':   id_counter, 
									  'name': names.get(end, end) }
						if types.get(end, 0) != 0:
							data[end].update({'type': types[end]})
						id_counter += 1

					start_id = str(data[start]['id'])
					end_id = str(data[end]['id'])

					c.write(start_id + '\t' + end_id + '\tLINKS_TO\n')

				counter -= 1

			else:
				break

	write_nodes(sorted(data.values(), key=lambda k: k['id']))

def write_nodes(data):

	print "Writing 'nodes.csv'..."

	with open('nodes.csv', 'wb+') as d:
		d.write('node\tname\tl:label\n')
		for value in data:

			node = str(value['id'])
			name = value['name']
			label = 'Page'

			if value.get('type', 0) != 0:
				label = label + ',' + value['type']

			d. write(node + '\t' + name + '\t' + label + '\n')

if __name__ == "__main__":
	parse_links()