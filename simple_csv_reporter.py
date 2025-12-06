# test_framework_with_timing.py
import unittest
import csv
import json
import time
from datetime import datetime

class SubTestResult(unittest.TextTestResult):
    """Simple TestResult with timing statistics."""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        
        # Statistics
        self.stats = {
            'total_main_tests': 0,      # Total test cases
            'total_subtests': 0,        # Total subtests
            'passed': 0,                # Total passed
            'failed': 0,                # Total failed
            'errors': 0,                # Total errors
            'skipped': 0,               # Total skipped
            
            # Lists for tracking
            'skipped_tests': [],        # List of skipped tests
            'failed_tests': [],         # List of failed tests
            'error_tests': [],          # List of error tests
        }
        
        # Determine if CSV output is enabled
        csv_filename = 'test_results.csv'
        self.csv_enabled = csv_filename is not None
        
        if self.csv_enabled:
            # Use provided filename
            self.csv_filename = csv_filename
            # Create CSV file
            self.csv_file = open(self.csv_filename, 'w', newline='', encoding='utf-8')
            self.writer = csv.writer(self.csv_file)
            
            # CSV headers (without test_type and subtest_name, with execution_time_ms)
            self.writer.writerow([
                'test_case_name',
                'test_function',
                'args',
                'return_value',
                'final_result',
                'skip_reason',
                'execution_time_ms'
            ])
        else:
            self.csv_filename = None
            self.csv_file = None
            self.writer = None
        
        # Dictionary to store start time for each test
        self.test_start_times = {}
    
    def startTest(self, test):
        super().startTest(test)
        self.stats['total_main_tests'] += 1
        
        # Save test start time
        self.test_start_times[test.id()] = time.time()
        
        if not hasattr(test, '_test_data'):
            test._test_data = {}
    
    def _calculate_execution_time(self, test):
        """Calculate test execution time."""
        if test.id() in self.test_start_times:
            start_time = self.test_start_times[test.id()]
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds
            return execution_time_ms
        return 0.0
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.stats['passed'] += 1
        if self.csv_enabled:
            execution_time = self._calculate_execution_time(test)
            self._write_result(test, 'PASSED', execution_time=execution_time)
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stats['failed'] += 1
        self.stats['failed_tests'].append(test.id())
        if self.csv_enabled:
            execution_time = self._calculate_execution_time(test)
            self._write_result(test, 'FAILED', execution_time=execution_time)
    
    def addError(self, test, err):
        super().addError(test, err)
        self.stats['errors'] += 1
        self.stats['error_tests'].append(test.id())
        if self.csv_enabled:
            execution_time = self._calculate_execution_time(test)
            self._write_result(test, 'ERROR', execution_time=execution_time)
    
    def addSkip(self, test, reason):
        """Handle skipped test."""
        super().addSkip(test, reason)
        self.stats['skipped'] += 1
        self.stats['skipped_tests'].append({
            'test_name': test.id(),
            'reason': reason
        })
        if self.csv_enabled:
            execution_time = self._calculate_execution_time(test)
            self._write_result(test, 'SKIPPED', execution_time=execution_time, skip_reason=reason)
    
    def addSubTest(self, test, subtest, outcome):
        super().addSubTest(test, subtest, outcome)
        self.stats['total_subtests'] += 1
        
        # Get subtest description (but not used in CSV)
        subtest_desc = getattr(subtest, '_subDescription', lambda: '')()
        
        # Determine status
        if outcome is None:
            status = 'PASSED'
            self.stats['passed'] += 1
        else:
            if outcome[0] == self.FAILURE:
                status = 'FAILED'
                self.stats['failed'] += 1
            else:
                status = 'ERROR'
                self.stats['errors'] += 1
        
        # Write result if CSV is enabled
        if self.csv_enabled:
            execution_time = self._calculate_execution_time(test)
            self._write_result(test, status, execution_time=execution_time)
    
    def _write_result(self, test, status, execution_time=0.0, skip_reason=''):
        """Write result to CSV."""
        if not self.csv_enabled:
            return
            
        # Get test data
        data = getattr(test, '_test_data', {})
        
        # Format args
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        all_args = list(args) + [f'{k}={v}' for k, v in kwargs.items()]
        
        self.writer.writerow([
            test.id(),                          # test_case_name
            test._testMethodName,               # test_function
            str(all_args),                      # args
            str(data.get('return_value', '')),  # return_value
            status,                             # final_result
            skip_reason,                        # skip_reason
            round(execution_time, 2)            # execution_time_ms (rounded to 2 decimal places)
        ])
        self.csv_file.flush()
    
    def print_summary(self):
        """Print simple summary to terminal."""
        # Calculate total executed tests (excluding skipped)
        total_tests_executed = (
            self.stats['passed'] + 
            self.stats['failed'] + 
            self.stats['errors']
        )
        
        total_tests_all = total_tests_executed + self.stats['skipped']
        
        if total_tests_executed > 0:
            success_rate = (self.stats['passed'] / total_tests_executed) * 100
        else:
            success_rate = 0
        
        print("\n" + "="*60)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*60)
        
        # Print statistics
        print(f"\n📈 TEST COUNTS:")
        print(f"   Test Cases:         {self.stats['total_main_tests']}")
        print(f"   Subtests:           {self.stats['total_subtests']}")
        print(f"   ───────────────────────────────")
        print(f"   ✅ Passed:          {self.stats['passed']}")
        print(f"   ❌ Failed:          {self.stats['failed']}")
        print(f"   ⚠️  Errors:          {self.stats['errors']}")
        print(f"   ⏭️  Skipped:         {self.stats['skipped']}")
        print(f"   Total Tests:        {total_tests_all}")
        print(f"   Executed Tests:     {total_tests_executed}")
        print(f"   Success Rate:       {success_rate:.1f}%")
        
        # Print skipped tests
        if self.stats['skipped_tests']:
            print(f"\n⏭️  SKIPPED TESTS ({len(self.stats['skipped_tests'])}):")
            for skip_info in self.stats['skipped_tests']:
                print(f"   • {skip_info['test_name']}")
                print(f"     Reason: {skip_info['reason']}")
        
        # Print failed tests
        if self.stats['failed_tests']:
            print(f"\n❌ FAILED TESTS ({len(self.stats['failed_tests'])}):")
            for test_name in self.stats['failed_tests']:
                print(f"   • {test_name}")
        
        # Print error tests
        if self.stats['error_tests']:
            print(f"\n⚠️  ERROR TESTS ({len(self.stats['error_tests'])}):")
            for test_name in self.stats['error_tests']:
                print(f"   • {test_name}")
        
        # Print file info
        print(f"\n💾 OUTPUT FILES:")
        if self.csv_enabled:
            print(f"   CSV Results:        {self.csv_filename}")
        else:
            print(f"   CSV Results:        Disabled")
        
        # Save summary to JSON file
        summary_data = {
            'statistics': self.stats.copy(),
            'success_rate_percent': success_rate,
            'csv_enabled': self.csv_enabled,
            'csv_filename': self.csv_filename if self.csv_enabled else None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Remove lists from stats for cleaner JSON
        summary_data['statistics'].pop('skipped_tests', None)
        summary_data['statistics'].pop('failed_tests', None)
        summary_data['statistics'].pop('error_tests', None)
        
        json_filename = 'test_summary.json'
        with open(json_filename, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"   JSON Summary:       {json_filename}")
        print("\n" + "="*60)
    
    def stopTestRun(self):
        """Override to print summary."""
        super().stopTestRun()
        self.print_summary()
        if self.csv_enabled:
            self.csv_file.close()