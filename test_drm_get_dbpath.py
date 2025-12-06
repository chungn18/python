# test_drm_get_dbpath.py
import unittest
from simple_csv_reporter import SubTestResult

class TestDrmGetDBPath(unittest.TestCase):
    """Test case của bạn."""
    
    def setUp(self):
        super().setUp()
        if not hasattr(self, '_test_data'):
            self._test_data = {}
    
    def test_simple_success(self):
        """Test thành công."""
        self._test_data['args'] = ['user1', 'device1']
        result = {'status': 'success', 'db_path': '/path/user1.db'}
        self._test_data['return_value'] = result
        self.assertEqual(result['status'], 'success')
    
    def test_with_subtests(self):
        """Test với subtests."""
        cases = ['admin', 'user', 'guest']
        
        for role in cases:
            with self.subTest(role=role):
                self._test_data['args'] = [f'{role}_user', f'{role}_device']
                result = {'status': 'success', 'role': role}
                self._test_data['return_value'] = result
                self.assertEqual(result['role'], role)
    
    def test_failure_case(self):
        """Test bị failed."""
        self._test_data['args'] = ['user1', 'device1']
        self._test_data['return_value'] = {'status': 'failed'}
        self.assertEqual(1, 2)  # Cố tình fail
    
    def test_error_case(self):
        """Test bị error."""
        self._test_data['args'] = ['user1', 'device1']
        # Cố tình gây lỗi
        raise ValueError("Test error case")
    
    def test_more_subtests(self):
        """Thêm subtests để test statistics."""
        for i in range(3):
            with self.subTest(index=i):
                self._test_data['args'] = [i]
                self._test_data['return_value'] = i * 2
                self.assertEqual(i * 2, i * 2)


# Chạy tests
if __name__ == '__main__':
    print("🚀 Running DRM Get DB Path Tests...")
    print("="*60)
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.resultclass = SubTestResult
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDrmGetDBPath)
    
    result = runner.run(suite)