#!/usr/bin/env python
# gen-or1k-sprs.py -- Generate OR1K SPR header from XML definition

# Copyright (c) 2014 OpenRISC Project Maintainers
# All rights reserved.
#
# Contributed by Peter Gavin <pgavin@gmail.com>.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following condition
# is met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.


import sys
import os
import xml.etree.ElementTree
import subprocess
import time

copyright = '''\
/* or1k-sprs.h -- OR1K SPR definitions
   Copyright (c) 2014 OpenRISC Project Maintainers
   All rights reserved.
   
   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following condition
   is met:
   
   1. Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
   
   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
   FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
   COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
   INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
   (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
   STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
   OF THE POSSIBILITY OF SUCH DAMAGE.
   */
'''

namespace_prefix = 'OR1K_SPR'

index_lsb = 0
index_msb = 10
index_bits = index_msb-index_lsb+1
group_lsb = 11
group_msb = 15
group_bits = group_msb-group_lsb+1

def gen_bit(output, tree, group_name, reg_name):
    
    name = tree.attrib['name']
    prefix = '{0:}_{1:}_{2:}_{3:}'.format(namespace_prefix,
                                          group_name.upper(),
                                          reg_name.upper(),
                                          name.upper(),
                                          )
    offset = int(tree.attrib['offset'], 0)
    mask = 1 << offset
    
    output.write('/* {} */\n'.format(tree.attrib['description']))

    output.write('#define {0:}_OFFSET {1:d}\n'.format(prefix, offset))
    output.write('#define {0:}_MASK   0x{1:08x}\n'.format(prefix, mask))
    output.write('#define {0:}_GET(X) (((X) >> {1:d}) & 0x1)\n'.format(prefix, offset))
    output.write('#define {0:}_SET(X, Y) (((X) & OR1K_UNSIGNED(0x{1:08x})) | ((!!(Y)) << {2:d}))\n'.format(prefix, mask ^ 0xffffffff, offset))
    output.write('\n')

def gen_field(output, tree, group_name, reg_name):
    
    name = tree.attrib['name']
    prefix = '{0:}_{1:}_{2:}_{3:}'.format(namespace_prefix,
                                          group_name.upper(),
                                          reg_name.upper(),
                                          name.upper(),
                                          )
    lsb = int(tree.attrib['lsb'], 0)
    msb = int(tree.attrib['msb'], 0)
    bits = msb-lsb+1
    mask = ((1 << bits) - 1) << lsb
    
    output.write('/* {} */\n'.format(tree.attrib['description']))

    output.write('#define {0:}_LSB    {1:d}\n'.format(prefix, lsb))
    output.write('#define {0:}_MSB    {1:d}\n'.format(prefix, msb))
    output.write('#define {0:}_BITS   {1:d}\n'.format(prefix, bits))
    output.write('#define {0:}_MASK   OR1K_UNSIGNED(0x{1:08x})\n'.format(prefix, mask))
    output.write('#define {0:}_GET(X) (((X) >> {1:d}) & OR1K_UNSIGNED(0x{2:08x}))\n'.format(prefix, lsb, ((1 << bits) - 1)))
    output.write('#define {0:}_SET(X, Y) (((X) & OR1K_UNSIGNED(0x{1:08x})) | ((Y) << {2:d}))\n'.format(prefix, mask ^ 0xffffffff, lsb))
    output.write('\n')

def gen_reg(output, tree, group_name, group_index):
    
    name = tree.attrib['name']
    prefix = '{0:}_{1:}_{2:}'.format(namespace_prefix,
                                         group_name.upper(),
                                         name.upper(),
                                         )
    index = int(tree.attrib['index'], 0)
    addr  = (group_index << group_lsb) | index

    output.write('/* {} */\n'.format(tree.attrib['description']))
    
    output.write('#define {0:}_INDEX OR1K_UNSIGNED(0x{1:03x})\n'.format(prefix, index))
    output.write('#define {0:}_ADDR  OR1K_UNSIGNED(0x{1:04x})\n'.format(prefix, addr))
    output.write('\n')

    for child in tree:
        
        if child.tag == 'bit':
            gen_bit(output, child, group_name, name)
        elif child.tag == 'field':
            gen_field(output, child, group_name, name)
        else:
            raise Exception('invalid tag `{0:}\', expecting `bit\' or `field\''.format(child.tag))

    output.write('\n')
    
def gen_reg_range(output, tree, group_name, group_index, outer_ranges = []):
    
    name = tree.attrib['name']
    prefix = '{0:}_{1:}_{2:}'.format(namespace_prefix,
                                               group_name.upper(),
                                               name.upper())
    base = int(tree.attrib['base'], 0)
    count = int(tree.attrib['count'], 0)
    step = int(tree.attrib.get('step', '1'), 0)
    addr_base = (group_index << group_lsb) | base

    output.write('/* {} */\n'.format(tree.attrib['description']))
    
    output.write('#define {0:}_BASE     OR1K_UNSIGNED(0x{1:03x})\n'.format(prefix, base))
    output.write('#define {0:}_COUNT    OR1K_UNSIGNED(0x{1:03x})\n'.format(prefix, count))
    output.write('#define {0:}_STEP     OR1K_UNSIGNED(0x{1:03x})\n'.format(prefix, step))

    output.write('#define {0:}_INDEX(N) ({0:}_BASE + ((N) * {0:}_STEP))\n'.format(prefix))
    output.write('#define {0:}_ADDR(N)  (({1:}_{2:} << {1:}_GROUP_SHIFT) | {0:}_INDEX(N))\n'.format(prefix,
                                                                                                    namespace_prefix,
                                                                                                    group_name.upper()))

    output.write('\n')

    for child in tree:
        
        if child.tag == 'bit':
            gen_bit(output, child, group_name, name)
        elif child.tag == 'field':
            gen_field(output, child, group_name, name)
        else:
            raise Exception('invalid tag `{0:}\', expecting `bit\' or `field\''.format(child.tag))

    output.write('\n')

def gen_reg_range_in_multi(output, tree, group_name, group_index, ranges):

    name = tree.attrib['name']
    new_ranges = ranges[:]
    new_ranges.append(name)

    parent_prefix = '{0:}_{1:}_{2:}'.format(namespace_prefix,
                                            group_name.upper(),
                                            '_'.join(n.upper() for n in ranges))
    prefix = '{0:}_{1:}'.format(parent_prefix, name.upper())

    base = int(tree.attrib['base'], 0)
    count = int(tree.attrib['count'], 0)
    step = int(tree.attrib.get('step', '1'), 0)

    output.write('/* {} */\n'.format(tree.attrib['description']))
    
    output.write('#define {0:}_BASE  OR1K_UNSIGNED(0x{1:03x})\n'.format(prefix, base))
    output.write('#define {0:}_COUNT OR1K_UNSIGNED(0x{1:03x})\n'.format(prefix, count))
    output.write('#define {0:}_STEP  OR1K_UNSIGNED(0x{1:03x})\n'.format(prefix, step))
    output.write('\n')

    parent_args = ', '.join('N{:d}'.format(n) for n in xrange(len(ranges)))
    args = ', '.join((parent_args, 'N{:d}'.format(len(ranges))))

    output.write('#define {0:}_INDEX({2:}) ({1:}_SUBBASE({3:}) + {0:}_BASE + ((N{4:d}) * {0:}_STEP))\n'.format(prefix,
                                                                                                               parent_prefix,
                                                                                                               args,
                                                                                                               parent_args,
                                                                                                               len(ranges)))
    output.write('#define {0:}_ADDR({3:})  (({1:}_{2:}_GROUP << {1:}_GROUP_SHIFT) | {0:}_INDEX({3:}))\n'.format(prefix,
                                                                                                                namespace_prefix,
                                                                                                                group_name.upper(),
                                                                                                                args))
    
    output.write('\n')

    reg_name = '_'.join(ranges + [name])

    for child in tree:
        
        if child.tag == 'bit':
            gen_bit(output, child, group_name, reg_name)
        elif child.tag == 'field':
            gen_field(output, child, group_name, reg_name)
        else:
            raise Exception('invalid tag `{0:}\', expecting `bit\' or `field\''.format(child.tag))
    
    
def gen_multi_reg_range(output, tree, group_name, group_index, ranges):

    name = tree.attrib['name']
    new_ranges = ranges[:]
    new_ranges.append(name)

    prefix = '{0:}_{1:}_{2:}'.format(namespace_prefix,
                                     group_name.upper(),
                                     '_'.join(n.upper() for n in new_ranges))
    base = int(tree.attrib['base'], 0)
    count = int(tree.attrib['count'], 0)
    step = int(tree.attrib.get('step', '1'), 0)

    output.write('/* {} */\n'.format(tree.attrib['description']))
    
    output.write('#define {0:}_BASE  OR1K_UNSIGNED(0x{1:03x})\n'.format(prefix, base))
    output.write('#define {0:}_COUNT OR1K_UNSIGNED(0x{1:03x})\n'.format(prefix, count))
    output.write('#define {0:}_STEP  OR1K_UNSIGNED(0x{1:03x})\n'.format(prefix, step))

    if len(ranges) > 0:
        parent_prefix = '{0:}_{1:}_{2:}'.format(namespace_prefix,
                                                group_name.upper(),
                                                '_'.join(n.upper for n in ranges))
        parent_args = ', '.join('N{:d}'.format(n) for n in xrange(len(ranges)))
        args = ', '.join((parent_args, 'N{:d}'.format(len(ranges)+1)))
        subbase = '{0:}_SUBBASE({1:}) + {2:}_BASE + ((N{3:d})*{2:}_STEP)'.format(parent_prefix,
                                                                                 parent_args,
                                                                                 prefix,
                                                                                 len(ranges),
                                                                                 )
    else:
        args = 'N0'
        subbase = '{0:}_BASE + ((N0)*{0:}_STEP)'.format(prefix)

    output.write('#define {0:}_SUBBASE({1:}) ({2:})\n'.format(prefix,
                                                              args,
                                                              subbase,
                                                              ))
    output.write('\n')

    for child in tree:
        
        if child.tag == 'multi-reg-range':
            gen_multi_reg_range(output, child, group_name, group_index, new_ranges)
        elif child.tag == 'reg-range':
            gen_reg_range_in_multi(output, child, group_name, group_index, new_ranges)
        else:
            raise Exception('invalid tag `{0:}\', expecting `bit\' or `field\''.format(child.tag))

    output.write('\n')
    
def gen_group(output, tree):

    group_name = tree.attrib['name']
    group_prefix = '{0:}_{1:}'.format(namespace_prefix, group_name.upper())
    group_index = int(tree.attrib['index'], 0)
    
    output.write('/**{}**/\n'.format('*' * len(tree.attrib['description'])))
    output.write('/* {} */\n'.format(tree.attrib['description']))
    output.write('/**{}**/\n'.format('*' * len(tree.attrib['description'])))

    output.write('#define {0:}_GROUP 0x{1:02x}\n'.format(group_prefix, group_index))
    output.write('\n')

    for child in tree:
        if child.tag == 'reg':
            gen_reg(output, child, group_name, group_index)
        elif child.tag == 'reg-range':
            gen_reg_range(output, child, group_name, group_index)
        elif child.tag == 'multi-reg-range':
            gen_multi_reg_range(output, child, group_name, group_index, [])
        else:
            raise Exception('invalid tag `{0:}\', expecting `reg\', `reg-range\', or `multi-reg-range\''.format(child.tag))

def gen_root(output, root, gitrev):

    gentime = time.strftime("%c")

    if gitrev != None:
        generated = "/*\n * Generated from revision %s *  on %s\n */\n" % (gitrev, gentime)
    else:
        generated = "/*\n * Generated on %s\n */\n" % (gentime)

    output.write(copyright)
    output.write('\n')
    output.write(generated)
    output.write('\n')
    output.write('#ifndef _OR1K_SPRS_H_\n')
    output.write('#define _OR1K_SPRS_H_\n')
    output.write('\n')
    output.write('#define {0:}_GROUP_BITS  {1:2d}\n'.format(namespace_prefix, group_bits))
    output.write('#define {0:}_GROUP_LSB   {1:2d}\n'.format(namespace_prefix, group_lsb))
    output.write('#define {0:}_GROUP_MSB   {1:2d}\n'.format(namespace_prefix, group_msb))
    output.write('#define {0:}_INDEX_BITS  {1:2d}\n'.format(namespace_prefix, index_bits))
    output.write('#define {0:}_INDEX_LSB   {1:2d}\n'.format(namespace_prefix, index_lsb))
    output.write('#define {0:}_INDEX_MSB   {1:2d}\n'.format(namespace_prefix, index_msb))
    output.write('\n')

    output.write('#ifdef __ASSEMBLER__\n')
    output.write('#define OR1K_UNSIGNED(x) x\n')
    output.write('#else\n')
    output.write('#define OR1K_UNSIGNED(x) x##U\n')
    output.write('#endif\n')

    output.write('\n')
    output.write('\n')

    group_names = set()

    for child in root:
        if child.tag == 'group':
            try:
                group_name = child.attrib['name']
            except:
                raise Exception('`group\' tag requires `name\' attribute')
            if group_name in group_names:
                raise Exception('duplicate group name: `{0:}\''.format(group_name))
            group_names.add(group_name)
            gen_group(output, child)
        else:
            raise Exception('invalid tag `{0:}\', expecting `group\''.format(child.tag))

    output.write('#endif\n')

if __name__ == '__main__':

    if len(sys.argv) > 2:
        raise Exception('too many arguments')
    if len(sys.argv) > 1:
        xml_file = sys.argv[1]
        dir = os.path.dirname(xml_file)
        gitrev = subprocess.check_output("cd %s; git rev-parse HEAD" % dir, shell=True)
    else:
        xml_file = sys.stdin
        gitrev = None
    
    root = xml.etree.ElementTree.parse(xml_file).getroot()

    if root.tag != "or1k-sprs":
        raise Exception('invalid root tag: `{0:}\''.format(root.tag))


    gen_root(sys.stdout, root, gitrev)
