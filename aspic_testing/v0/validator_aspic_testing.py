#!/usr/bin/env python
import lcatr.schema
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
    def _test_type(self, line):
        return line.split()[4]
    def run_validator(self, test_type, stanza):
        exec("result = self.validate%s(stanza)" % self._mapping[test_type])
        return result
    def process_file(self):
        lines = open(self.summary_file).readlines()
        all_results = []
        stanza = None
        j = 1
        i = self._read_file_header(lines)
        while (i < len(lines)):
            if lines[i].startswith('chip') :
                if stanza is not None:
                    # Process the existing stanza
                    j+=1
                    all_results.append(self.run_validator(test_type, stanza))
                test_type = self._test_type(lines[i])
                stanza = []
            if lines[i].strip() != '':
                # Add non-empty lines to current stanza
                stanza.append(lines[i])
            i += 1
        #need to run the very last stanza separately, as the files
        #do not stop with a line starting with 'chip'.
        all_results.append(self.run_validator(test_type, stanza))
        print "number of stanzas processed : ", j
        lcatr.schema.write_file(all_results)
        lcatr.schema.validate_file()

    def _read_file_header(self, lines):
        header = []
        i=0
        while (lines[i].startswith('#') ):
            header.append(lines[i])
            i=i+1
        #this is temporary : we should be doing something with the header?
        return i
    def _parse_header_line(self, line):
        tokens = line.split()
        data = {'chip_id' : tokens[0],
                'GAIN' : tokens[1][1:],
                'RC' : tokens[2][2:],
                'clock_file' : tokens[3],
                'test_type' : tokens[4],
                'attenuator_start' : tokens[5],
                'data_file' : tokens[7],
                'activity_description' : ' '.join(tokens[8:])}

        relpath = os.path.join(self.rawfile_path,data['data_file'])
        print relpath, os.path.exists(relpath)
        lcatr.schema.fileref.make(os.path.relpath(relpath))
        return data
    def validate_temp(self, stanza):
        data = self._parse_header_line(stanza[0])
        data['test_passed'] = stanza[1].startswith('Passed')
        data['temperature'] = float(stanza[3].strip())
        data['power_level'] = float(stanza[4].strip())
        return validate('aspic_temp', **data)
    def validate_channel(self, stanza):
        data = self._parse_header_line(stanza[0])
        data['BEB_temperature'] = 0.  # to be filled
        data['test_passed'] = stanza[1].startswith('Passed')
        for i in range(0, 8):
            data['channel_%02i' % i] = float(stanza[3 + i].split()[0])
        return validate('aspic_channel_info', **data)
    def validate_noise(self, stanza):
        data = self._parse_header_line(stanza[0])
        data['test_passed'] = stanza[1].startswith('Passed')
        data['BEB_temperature'] = 0.  # to be filled
        for i, value in zip(range(8), stanza[3].split()):
            data['channel_%02i' % i] = float(value)
        return validate('aspic_noise_info', **data)
    def validate_pass_fail(self, stanza):
        data = self._parse_header_line(stanza[0])
        data['BEB_temperature'] = 0.  # to be filled
        data['test_passed'] = stanza[1].startswith('Passed')
        return validate('aspic_pass_fail', **data)

if __name__ == "__main__":
    import sys, glob
    from lcatr.harness import config

    print "executing validator_test_job.py"
    cfg=config.Config()
    #defined as a symlink by the producer script
    basedir = os.environ['ASPIC_BASE_DIR']
    input_file = glob.glob(os.path.join(basedir,"Logs","log-%s-*.txt"%cfg.unit_id))[0]
    input_info=os.path.basename(input_file).split('-')
    raw_path = os.path.join("CHIP%s"%input_info[1],input_info[2],input_info[3].strip('.txt'))

    summary = SocketTestSummary(input_file, raw_path)
    summary.process_file()

