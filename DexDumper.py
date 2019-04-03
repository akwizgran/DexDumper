# -*- coding: utf-8 -*-
'''
Created on 2011-12-5

@author: Jinghao
'''
import struct
import zlib
import hashlib
import dexfile
import os
import sys
import DexError
import random
import zipfile
import fnmatch
from optparse import OptionParser
import shutil
import copy
import codecs

def unzip(apk_file):
    if not os.path.exists(apk_file):
        print 'The APK file is not exist...'
        sys.exit(1)
    
    if zipfile.is_zipfile(apk_file):
        try:
            zip_file = zipfile.ZipFile(apk_file, 'r')
            zip_file.extract('classes.dex')
            for i in range (2, 100):
                try:
                    zip_file.extract('classes%d.dex' % i)
                except Exception,e:
                    continue
            return True
        except Exception,e:
            print 'Bad apk file..'
            return False

def dumper(dex_file, output_file):
    fw = codecs.open(output_file, 'w', 'utf-8')
    
    try:
        read_handle = open(dex_file, 'rb')
        dex_handle = dexfile.DexFile(read_handle)
    except DexError.DexError, e:
        #print '%s is invalid.'
        raise DexError.DexError('DEX file is invalid')
    
    string_start = dex_handle.get_string_start()
    string_list = dex_handle.get_string_list()
    string_size = dex_handle.get_string_size()
    
    seq = 0
    print string_start
    print string_size
    dex_handle.seek(string_start)
    temp = ''
    size_tag = True
    string_tag = False
    while seq < string_size:
        value = dex_handle.read(1)
        if value == '\x00':
            #print struct.unpack('<%ds' % len(temp), temp)[0]
            #temp = struct.unpack('<%ds' % len(temp), temp)[0]
            
            fw.write(temp.encode('string_escape') + '\n')
            temp = ''
            size_tag = True
            string_tag = False
            continue
        if size_tag:
            if struct.unpack('<b', value)[0] < 0:
                seq += 1
                continue
            else:
                size_tag = False
                string_tag = True
        
        if string_tag:
            if value != '\x00':
                temp += value
                seq += 1
                continue
        seq += 1
    
    fw.close()
    print 'Dump finished...'
    
    
    
    
def main():
    usage = 'usage: DexDumper -i INPUT_FILE {-o OUTPUT_FILE}'
    parser = OptionParser(usage)
    parser.add_option('-i', '--input', dest='input_file',
                      default=None,
                      help='Input file for APKs')
    parser.add_option('-o', '--output', dest='output_file',
                      default='output.txt',
                      help='[Optional]Output file for dex info')
        
    options, args = parser.parse_args()
    
    if options.input_file:
        input_file = options.input_file
    else:
        print usage
        sys.exit(1)
        
    if options.output_file == 'output.txt':
        output_file = 'output.txt'
    else:
        output_file = options.output_file
    
    if not os.path.exists(input_file):
        print 'Input file is not exist.'
        sys.exit(1)
    
    if unzip(input_file):
        dumper('classes.dex', output_file)
        for i in range(2, 100):
            if os.path.exists('classes%d.dex' % i):
                dumper('classes%d.dex' % i, '%s.%d' % (output_file, i))
    else:
        sys.exit(1)
            


if __name__ == '__main__':
    main()
