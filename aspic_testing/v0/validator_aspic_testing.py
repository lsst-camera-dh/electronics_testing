#!/usr/bin/env python
import lcatr.schema
import siteUtils
import os

def validate(schema, **kwds):
    results = lcatr.schema.valid(lcatr.schema.get(schema), **kwds)
    return results

class SocketTestSummary(object):
    _mapping = {'TEMP' : '_temp',
                'GAIN' : '_channel',
                'NOISE' : '_noise',
                'LINEAR18' : '_channel',
                'LINEAR16' : '_pass_fail',
                'XTALK' : '_pass_fail',
                'CONSO' : '_pass_fail'}
    def __init__(self, summary_file, rawfile_path):
        self.summary_file = summary_file
        self.rawfile_path = rawfile_path
        #needs to take a decision on where to put the summary_file
        #for now it stays at the top of the directory structure in the database
        #relpath = os.path.join(self.rawfile_path, self.summary_file)
        relpath = summary_file
        #fileref = lcatr.schema.fileref.make(relpath)
        self.all_results = []#[fileref]
    def _test_type(self, line):
        return line.split()[4]
    def run_validator(self, test_type, stanza):
        exec("self.validate%s(stanza)" % self._mapping[test_type])
    def process_file(self):
        lines = open(self.summary_file).readlines()
        stanza = None
        j = 1
        i = self._read_file_header(lines)
        while (i < len(lines)):
            if lines[i].startswith('chip') :
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
        #need to run the very last stanza separately, as the files
        #do not stop with a line starting with 'chip'.
        self.run_validator(test_type, stanza)
        print "number of stanzas processed : ", j
        lcatr.schema.write_file(self.all_results)
        lcatr.schema.validate_file()

    def _read_file_header(self, lines):
        i=0
        data = {'summary_file':os.path.basename(self.summary_file)}
        while (lines[i].startswith('#') ):
            line=lines[i]
            if line.startswith('#setup'):
                data['activity_location'] = line.split()[1]
            if line.startswith('#step'):
                data['activity_type'] = line.split()[1]
            if 'timestamp' in line:
                data['acquistion_start_time'] = line.split()[1].strip()
            if 'chip' in line:
                data['chip_id'] =line.split()[1].strip()
            if line.startswith('#VI'):
                data['software_version'] = line[line.find('_v'):].strip('.vi\n')[1:]
            i=i+1
        data['status'] = lines[-1].split()[1]
        self.all_results.append(lcatr.schema.valid(lcatr.schema.get('aspic_activity'), **data))
        return i
    def _parse_header_line(self, line):
        tokens = line.split()
        data = {'chip_id' : tokens[0],
                'GAIN' : tokens[1],
                'RC' : tokens[2],
                'clock_file' : tokens[3],
                'test_type' : tokens[4],
                'BEB_temperature' : tokens[5][2:],
                'attenuator_start' : tokens[6],
                'data_file' : tokens[7],
                'activity_description' : ' '.join(tokens[8:])}

        relpath = os.path.join(self.rawfile_path,data['data_file'])
        fileref = lcatr.schema.fileref.make(os.path.relpath(relpath))
        return data, fileref
    def validate_temp(self, stanza):
        data, fileref = self._parse_header_line(stanza[0])
        data['test_passed'] = stanza[1].startswith('Passed')
        data['temperature'] = float(stanza[3].strip())
        data['power_level'] = float(stanza[4].strip())
        #self.all_results.extend([validate('aspic_temp', **data), fileref])
        self.all_results.extend([validate('aspic_temp', **data)])
    def validate_channel(self, stanza):
        data, fileref = self._parse_header_line(stanza[0])
        data['test_passed'] = stanza[1].startswith('Passed')
        for i in range(0, 8):
            data['channel_%02i' % i] = float(stanza[3 + i].split()[0])
        #self.all_results.extend([validate('aspic_channel_info', **data), fileref])
        self.all_results.extend([validate('aspic_channel_info', **data)])
    def validate_noise(self, stanza):
        data, fileref = self._parse_header_line(stanza[0])
        data['test_passed'] = stanza[1].startswith('Passed')
        for i, value in zip(range(8), stanza[3].split()):
            data['channel_%02i' % i] = float(value)
        #self.all_results.extend([validate('aspic_noise_info', **data), fileref])
        self.all_results.extend([validate('aspic_noise_info', **data)])
    def validate_pass_fail(self, stanza):
        data, fileref = self._parse_header_line(stanza[0])
        data['test_passed'] = stanza[1].startswith('Passed')
        #self.all_results.extend([validate('aspic_pass_fail', **data), fileref])
        self.all_results.extend([validate('aspic_pass_fail', **data)])

if __name__ == "__main__":
    import sys, glob
    from lcatr.harness import config

    print "executing validator_test_job.py"
    cfg=config.Config()
    #defined as a symlink by the producer script
    input_file = glob.glob("log-%s-*.txt"%cfg.unit_id)[0]
    print "Reading ", input_file
    input_info=os.path.basename(input_file).split('-')
    raw_path = os.path.join("CHIP%s"%input_info[1],input_info[2],input_info[3].strip('.txt'))

    summary = SocketTestSummary(input_file, raw_path)
    summary.process_file()

