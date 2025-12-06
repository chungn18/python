# test_drm_get_dbpath.py - FILE DUY NHẤT
import unittest
import csv
import json
import time
from datetime import datetime

class SubTestResult(unittest.TextTestResult):
    """TestResult với CSV reporting và terminal summary."""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        
        # Statistics
        self.stats = {
            'total_main_tests': 0,      # Tổng test cases
            'total_subtests': 0,        # Tổng subtests
            'total_passed': 0,          # Tổng passed (cả test và subtest)
            'total_failed': 0,          # Tổng failed
            'total_errors': 0,          # Tổng errors
            'failed_tests': [],         # List test failed
            'error_tests': [],          # List test error
            'start_time': time.time()   # Thời gian bắt đầu
        }
        
        # Tạo CSV file
        self.csv_file = open('test_results.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.csv_file)
        
        # Viết headers
        self.writer.writerow([
            'test_case_name', 'subtest_name', 'test_function',
            'args', 'return_value', 'final_result', 'timestamp'
        ])
    
    def startTest(self, test):
        super().startTest(test)
        self.stats['total_main_tests'] += 1
        if not hasattr(test, '_test_data'):
            test._test_data = {}
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.stats['total_passed'] += 1
        self._write_to_csv(test, '', 'PASSED')
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stats['total_failed'] += 1
        self.stats['failed_tests'].append(test.id())
        self._write_to_csv(test, '', 'FAILED')
    
    def addError(self, test, err):
        super().addError(test, err)
        self.stats['total_errors'] += 1
        self.stats['error_tests'].append(test.id())
        self._write_to_csv(test, '', 'ERROR')
    
    def addSubTest(self, test, subtest, outcome):
        super().addSubTest(test, subtest, outcome)
        self.stats['total_subtests'] += 1
        
        # Lấy tên subtest
        subtest_desc = getattr(subtest, '_subDescription', lambda: '')()
        
        # Xác định status
        if outcome is None:
            status = 'PASSED'
            self.stats['total_passed'] += 1
        else:
            if outcome[0] == self.FAILURE:
                status = 'FAILED'
                self.stats['total_failed'] += 1
            else:
                status = 'ERROR'
                self.stats['total_errors'] += 1
        
        # Ghi vào CSV
        self._write_to_csv(test, subtest_desc, status)
    
    def _write_to_csv(self, test, subtest_name, status):
        """Ghi kết quả vào CSV."""
        data = getattr(test, '_test_data', {})
        
        self.writer.writerow([
            test.id(),                              # test_case_name
            subtest_name,                           # subtest_name
            test._testMethodName,                   # test_function
            json.dumps(data.get('args', [])),       # args
            json.dumps(data.get('return_value', '')),  # return_value
            status,                                 # final_result
            datetime.now().isoformat()              # timestamp
        ])
        self.csv_file.flush()
    
    def print_summary(self):
        """In summary ra terminal."""
        end_time = time.time()
        duration = end_time - self.stats['start_time']
        
        # Tính tổng số tests đã chạy
        total_tests_run = (self.stats['total_main_tests'] + 
                          self.stats['total_subtests'])
        
        # Tính success rate
        total_successful = self.stats['total_passed']
        success_rate = (total_successful / total_tests_run * 100) if total_tests_run > 0 else 0
        
        print("\n" + "="*60)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*60)
        
        # In statistics
        print(f"\n📈 STATISTICS:")
        print(f"   Total Test Cases:    {self.stats['total_main_tests']}")
        print(f"   Total Subtests:      {self.stats['total_subtests']}")
        print(f"   Total Tests Run:     {total_tests_run}")
        print(f"   ───────────────────────────────")
        print(f"   ✅ Passed:           {self.stats['total_passed']}")
        print(f"   ❌ Failed:           {self.stats['total_failed']}")
        print(f"   ⚠️  Errors:           {self.stats['total_errors']}")
        print(f"   Success Rate:        {success_rate:.1f}%")
        print(f"   Execution Time:      {duration:.2f} seconds")
        
        # In failed tests
        if self.stats['failed_tests']:
            print(f"\n❌ FAILED TESTS ({len(self.stats['failed_tests'])}):")
            for test_name in self.stats['failed_tests']:
                print(f"   • {test_name}")
        
        # In error tests
        if self.stats['error_tests']:
            print(f"\n⚠️  ERROR TESTS ({len(self.stats['error_tests'])}):")
            for test_name in self.stats['error_tests']:
                print(f"   • {test_name}")
        
        # In file info
        print(f"\n💾 OUTPUT FILES:")
        print(f"   CSV Results:        test_results.csv")
        
        print("\n" + "="*60)
    
    def stopTestRun(self):
        """Override để in summary."""
        super().stopTestRun()
        self.print_summary()
        self.csv_file.close()