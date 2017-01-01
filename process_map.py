import xml.etree.ElementTree as ET
import re
from collections import defaultdict
import csv
import codecs

OSM_PATH = "..\project_OSM\Kolkata.osm"
#OSM_PATH = "Kolkata_sample.osm"
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"


NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

re_kolkata = re.compile(r'[kK][oO][lL][kK][aA][tT][aA]')

class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

"""  ----------------------------------
 Is this a postcode element? We are aware of issues in the postcode value.
 This calls for a special processing of the value whenver we encounter a
 tag element meant for postcode.
 ---------------------------------- """
def is_a_postcode(elem):
    return elem.attrib['k'] == 'addr:postcode'

"""  ----------------------------------
 Is this a city element? We want to make the city names uniform.
 ---------------------------------- """
def is_a_city(elem):
    return elem.attrib['k'] == 'addr:city'

""" ----------------------------------
 Is this a street element? We want to make the street names consistent.
 ---------------------------------- """
def is_a_street(elem):
    return elem.attrib['k'] == 'addr:street'

""" -------------------------------------------
Change the street name to be consistent
------------------------------------------ """
mapped_name = {'street':'Street', 'st.':'Street', 'st':'Street', 
               'road':'Road', 'rd':'Road', 'rd.':'Road', 'raod':'Road',
               'sarani':'Sarani', 'pally':'Pally',
               'avenue':'Avenue', 'ave':'Avenue', 'ave.':'Avenue', 'av':'Avenue', 'av.':'Avenue',
               'lane':'Lane', 'ln':'Lane', 'ln.':'Lane',
               'park':'Park', 'pk':'Park', 'pk.':'Park',
               'row':'Row'}
def update_street_name(street_name):
    words = street_name.split(" ")
    for i in range(len(words)):
        if words[i].lower() in mapped_name:
            words[i] = mapped_name[words[i].lower()]
    updated_street_name = " ".join(words)
    return updated_street_name

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  

    """ -----------------------------
     Process the 'node' elements rakesh
     ----------------------------- """
    if element.tag == "node":
        for myattrib_name, myattrib_val in element.attrib.iteritems():
            if myattrib_name in node_attr_fields:
                node_attribs[myattrib_name] = myattrib_val
        """ -------------------------------------------------------
         Iterate over all the tag elements of this 'node' element
         ------------------------------------------------------- """
        for tag_of_node in element.findall("tag"):
            tags_dict = {}
            for tag_of_node_attrib_name, tag_of_node_attrib_val in tag_of_node.attrib.iteritems():
                if tag_of_node_attrib_name == 'k':
                    if ':' in tag_of_node_attrib_val:
                        mylist = tag_of_node_attrib_val.split(':', 1)
                        tags_dict['type'] = mylist[0]
                        tags_dict['key'] = mylist[1]
                    else:
                        tags_dict['type'] = 'regular'
                        tags_dict['key'] = tag_of_node_attrib_val
                if tag_of_node_attrib_name == 'v':
                    """ -----------------------------
                     Check if this element is a postcode
                     ----------------------------- """
                    if is_a_postcode(tag_of_node):
                        raw_postcode = tag_of_node_attrib_val
                        """ -----------------------------------------------------
                         refine the postal code to make sure it is an integer
                         ----------------------------------------------------- """
                        postcode = re.sub(r'[^0-9]', '', raw_postcode)
                        tags_dict['value'] = postcode
                    elif is_a_city(tag_of_node):
                        m = re_kolkata.search(tag_of_node_attrib_val)
                        if m is not None:
                            tags_dict['value'] = 'Kolkata'
                        else:
                            tags_dict['value'] = tag_of_node_attrib_val
                    elif is_a_street(tag_of_node):
                        tags_dict['value'] = update_street_name(tag_of_node_attrib_val)
                    else:
                        tags_dict['value'] = tag_of_node_attrib_val
            tags_dict['id'] = node_attribs['id']
            tags.append(tags_dict)


    """ --------------------------
     Process the 'way' elements
     -------------------------- """
    if element.tag == "way":
        for myattrib_name, myattrib_val in element.attrib.iteritems():
            if myattrib_name in way_attr_fields:
                way_attribs[myattrib_name] = myattrib_val
        """ --------------------------------------------------------
         Iterate over all the 'tag' elements of this 'way' element
         ------------------------------------------------------- """
        for tag_of_way in element.findall("tag"):
            tags_dict = {}
            for tag_of_way_attrib_name, tag_of_way_attrib_val in tag_of_way.attrib.iteritems():
                if tag_of_way_attrib_name == 'k':
                    if ':' in tag_of_way_attrib_val:
                        mylist = tag_of_way_attrib_val.split(':', 1)
                        tags_dict['type'] = mylist[0]
                        tags_dict['key'] = mylist[1]
                    else:
                        tags_dict['type'] = 'regular'
                        tags_dict['key'] = tag_of_way_attrib_val
                if tag_of_way_attrib_name == 'v':
                    """ ------------------------------------
                     Check if this element is a postcode 
                     ------------------------------------ """
                    if is_a_postcode(tag_of_way):
                        raw_postcode = tag_of_way_attrib_val
                        """ -----------------------------------------------------
                         Refine the postal code to make sure it is an integer
                         ----------------------------------------------------- """
                        postcode = re.sub(r'[^0-9]', '', raw_postcode)
                        tags_dict['value'] = postcode
                    elif is_a_city(tag_of_way):
                        m = re_kolkata.search(tag_of_way_attrib_val)
                        if m is not None:
                            tags_dict['value'] = 'Kolkata'
                        else:
                            tags_dict['value'] = tag_of_way_attrib_val
                    elif is_a_street(tag_of_way):
                        tags_dict['value'] = update_street_name(tag_of_way_attrib_val)
                    else:
                        tags_dict['value'] = tag_of_way_attrib_val
            tags_dict['id'] = way_attribs['id']
            tags.append(tags_dict)

        
        nd_number = 0
        """ --------------------------------------------------------
         Iterate over all the 'nd' elements of this 'way' element
         ------------------------------------------------------- """
        for nd_of_way in element.findall("nd"):
            nds_dict = {}
            for nd_of_way_attrib_name, nd_of_way_attrib_val in nd_of_way.attrib.iteritems():
                if nd_of_way_attrib_name == 'ref':
                    nds_dict['node_id'] = nd_of_way_attrib_val
            nds_dict['id'] = way_attribs['id']
            nds_dict['position'] = nd_number
            nd_number = nd_number + 1
            way_nodes.append(nds_dict)

    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    

def get_element(osm_file, tags = ('node', 'way', 'relation')):
    context = ET.iterparse(osm_file, events = ('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
    
def process_map(file_in, validate):
    print "Creating csv files now ....."
    with codecs.open(NODES_PATH, 'w') as nodes_file, \
        codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
        codecs.open(WAYS_PATH, 'w') as ways_file, \
        codecs.open(WAY_NODES_PATH, 'w') as ways_nodes_file, \
        codecs.open(WAY_TAGS_PATH, 'w') as ways_tags_file :      
        
        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        nodes_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        ways_nodes_writer = UnicodeDictWriter(ways_nodes_file, WAY_NODES_FIELDS)
        ways_tags_writer = UnicodeDictWriter(ways_tags_file, WAY_TAGS_FIELDS)
        
        """ ----------------
         Will skip the header for now since we will create the tables in sqlite3
         ---------------- """

        for element in get_element(file_in, tags = ('node', 'way')):
            el = shape_element(element)
            if el:
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    nodes_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    ways_nodes_writer.writerows(el['way_nodes'])
                    ways_tags_writer.writerows(el['way_tags'])
                    
    print "All the csv files have been written"   
    
process_map(OSM_PATH, False)