import json
from xml.dom import minidom
import xml.etree.ElementTree as ET
import os
import glob

def set_xml(path):
    json_load = None
    with open(path, "r") as f:
        json_load = json.load(f)
        
    root = ET.Element("annotation")
    r_fo = ET.SubElement(root, "folder")
    dirname = os.path.dirname(path)
    r_fo.text = dirname[max(dirname.rfind(os.sep),dirname.rfind("/"))+1:]
    r_fi = ET.SubElement(root, "filenme")
    r_fi.text = os.path.basename(path)
    r_pa = ET.SubElement(root, "path")
    r_pa.text = "/" + r_fo.text + "/" + r_fi.text
    
    r_so = ET.SubElement(root, "source")
    so_da = ET.SubElement(r_so, "database")
    so_da.text = 'Unknown'
    
    r_si = ET.SubElement(root, "size")
    si_wi, si_he, si_de = ET.SubElement(r_si, "width"), ET.SubElement(r_si, "height"), ET.SubElement(r_si, "depth")
    si_wi.text, si_he.text, si_de.text = str(json_load["width"]),str(json_load["height"]),"3"
    
    r_se = ET.SubElement(root, "segment")
    r_se.text = '0'

    for lead in json_load["leads"]:
        name_format = lead["lead_name"]+ "_{}"
        for _type in ["text","lead"]:
            r_ob = ET.SubElement(root, "object")
            ob_na = ET.SubElement(r_ob, "name")
            ob_po = ET.SubElement(r_ob, "pose")
            ob_na.text, ob_po.text = name_format.format(_type),"Unspecified"
            ob_tr = ET.SubElement(r_ob, "truncated")
            ob_tr.text = '0'
            ob_di = ET.SubElement(r_ob, "difficult")
            ob_di.text = '0'
            ob_bn = ET.SubElement(r_ob, "bndbox")
            bn_xmin = ET.SubElement(ob_bn, "xmin")
            bn_ymin = ET.SubElement(ob_bn, "ymin")
            bn_xmax = ET.SubElement(ob_bn, "xmax")
            bn_ymax = ET.SubElement(ob_bn, "ymax")
            bbox = lead[_type+"_bounding_box"]["0"] + lead[_type+"_bounding_box"]["2"]
            bn_ymin.text, bn_xmin.text, bn_ymax.text, bn_xmax.text = [str(i) for i in bbox]
    return root


def main(root_path):
    paths = glob.glob(root_path+"*.json")
    for path in paths:
        root_xml = set_xml(path)
        doc = minidom.parseString(ET.tostring(root_xml, 'utf-8'))
        xml_path = os.path.splitext(path)[0] + ".xml"
        with open(xml_path, "w") as f:
            doc.writexml(f, encoding='utf-8', newl='\n', indent='', addindent='  ')
