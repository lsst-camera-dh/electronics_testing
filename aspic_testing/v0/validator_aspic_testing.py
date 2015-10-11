#!/usr/bin/env python
#import lcatr.schema
import os

def validate(schema, **kwds):
    pass
#    return lcatr.schema.valid(lcatr.schema.get(schema), **kwds)

class SocketTestSummary(object):
    _mapping = {'TEMP' : '_temp',
                'GAIN' : '_channel',
                'NOISE' : '_noise',
                'LINEAR18' : '_channel',
                'LINEAR16' : '_pass_fail',
                'XTALK' : '_pass_fail',
                'CONSO' : '_pass_fail'}
    def __init__(self, summary_file):
        self.summary_file = summary_file
    def _test_type(self, line):
        return line.split()[4]
    def run_validator(self, test_type, stanza):
        return eval("self.validate%s(stanza)" % self._mapping[test_type])
    def process_file(self):
        lines = open(self.summary_file).readlines()
        #stanzas = {}
        stanza = None
        i = 0
        j = 1
        while (i < len(lines)):
            if lines[i].startswith('chip'):
                if stanza is not None:
                    # Process the existing stanza
                    j+=1
                    self.run_validator(test_type, stanza)
                test_type = self._test_type(lines[i])
                stanza = []
            if lines[i].strip() != '':
                # Add non-empty lines to current stanza
                stanza.append(lines[i])
            i += 1
        print "number of stanzas processed : ", j
    def _parse_header_line(self, line):
        tokens = line.split()
        data = {'chip_id' : tokens[0],
                'GAIN' : tokens[1][1:],
                'RC' : tokens[2][2:],
                'clock_file' : tokens[3],
                'test_type' : tokens[4],
                'attenuator_start' : tokens[5],
                'data_file' : '_'.join(tokens[6:8]),
                'activity_description' : ' '.join(tokens[8:])}
        return data
    def validate_temp(self, stanza):
        data = self._parse_header_line(stanza[0])
        data['test_passed'] = stanza[1].startswith('Passed')
        data['temperature'] = float(stanza[3].strip())
        data['power_level'] = float(stanza[4].strip())
        validate('aspic_temp', **data)
    def validate_channel(self, stanza):
        data = self._parse_header_line(stanza[0])
        data['BEB_temperature'] = 0.  # to be filled
        data['test_passed'] = stanza[1].startswith('Passed')
        for i in range(0, 8):
            data['channel_%02i' % i] = float(stanza[3 + i].split()[0])
        validate('aspic_channel_info', **data)
    def validate_noise(self, stanza):
        data = self._parse_header_line(stanza[0])
        data['test_passed'] = stanza[1].startswith('Passed')
        for i, value in zip(range(8), stanza[3].split()):
            data['channel_%02i' % i] = float(value)
    def validate_pass_fail(self, stanza):
        data = self._parse_header_line(stanza[0])
        data['test_passed'] = stanza[1].startswith('Passed')


if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    summary = SocketTestSummary(filename)
    summary.process_file()

