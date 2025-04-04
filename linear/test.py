import unittest
from unittest.mock import patch, Mock
from query import fetch_linear_issues  # assuming the code is saved in fetch_linear_issues.py


class TestFetchAllIssues(unittest.TestCase):

    @patch("fetch_linear_issues.requests.post")
    def test_single_page_fetch(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "issues": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [{"id": "1"}]
                }
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = fetch_linear_issues.fetch_all_issues("fake-key")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "1")

    @patch("fetch_linear_issues.requests.post")
    def test_multiple_pages_fetch(self, mock_post):
        responses = [
            {
                "data": {
                    "issues": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                        "nodes": [{"id": "1"}]
                    }
                }
            },
            {
                "data": {
                    "issues": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": [{"id": "2"}]
                    }
                }
            }
        ]

        def side_effect(*args, **kwargs):
            response = Mock()
            response.json.return_value = responses.pop(0)
            response.raise_for_status = Mock()
            return response

        mock_post.side_effect = side_effect

        result = fetch_linear_issues.fetch_all_issues("fake-key")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "1")
        self.assertEqual(result[1]["id"], "2")

    @patch("fetch_linear_issues.requests.post")
    def test_raises_for_status_called(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "data": {
                "issues": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": []
                }
            }
        }
        mock_post.return_value = mock_response

        fetch_linear_issues.fetch_all_issues("fake-key")
        mock_response.raise_for_status.assert_called_once()

    @patch("fetch_linear_issues.requests.post")
    def test_correct_headers_sent(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "data": {
                "issues": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": []
                }
            }
        }
        mock_post.return_value = mock_response

        api_key = "test-key"
        fetch_linear_issues.fetch_all_issues(api_key)

        mock_post.assert_called_with(
            fetch_linear_issues.LINEAR_API_URL,
            json={"query": fetch_linear_issues.QUERY, "variables": {"after": None}},
            headers={"Authorization": api_key, "Content-Type": "application/json"}
        )

    @patch("fetch_linear_issues.requests.post")
    def test_query_structure(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "data": {
                "issues": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": []
                }
            }
        }
        mock_post.return_value = mock_response

        fetch_linear_issues.fetch_all_issues("key")
        self.assertIn("createdAt", fetch_linear_issues.QUERY)
        self.assertIn("labels", fetch_linear_issues.QUERY)
        self.assertIn("attachments", fetch_linear_issues.QUERY)

    @patch("fetch_linear_issues.requests.post")
    def test_handles_empty_issues(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "data": {
                "issues": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": []
                }
            }
        }
        mock_post.return_value = mock_response

        result = fetch_linear_issues.fetch_all_issues("key")
        self.assertEqual(result, [])

    @patch("fetch_linear_issues.requests.post")
    def test_page_cursor_updates(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "data": {
                "issues": {
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor123"},
                    "nodes": []
                }
            }
        }
        mock_post.return_value = mock_response

        fetch_linear_issues.fetch_all_issues("key")
        self.assertTrue(mock_post.call_args[1]["json"]["variables"]["after"] in [None, "cursor123"])

    @patch("fetch_linear_issues.requests.post")
    def test_api_key_required(self, mock_post):
        with self.assertRaises(TypeError):
            fetch_linear_issues.fetch_all_issues()

    @patch("fetch_linear_issues.requests.post")
    def test_invalid_json_structure(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"unexpected": "structure"}
        mock_post.return_value = mock_response

        with self.assertRaises(KeyError):
            fetch_linear_issues.fetch_all_issues("key")

    @patch("fetch_linear_issues.time.sleep", return_value=None)
    @patch("fetch_linear_issues.requests.post")
    def test_sleep_called_between_requests(self, mock_post, mock_sleep):
        responses = [
            {
                "data": {
                    "issues": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "next"},
                        "nodes": []
                    }
                }
            },
            {
                "data": {
                    "issues": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "nodes": []
                    }
                }
            }
        ]

        def side_effect(*args, **kwargs):
            response = Mock()
            response.raise_for_status = Mock()
            response.json.return_value = responses.pop(0)
            return response

        mock_post.side_effect = side_effect
        fetch_linear_issues.fetch_all_issues("key")
        mock_sleep.assert_called_once_with(0.5)


if __name__ == "__main__":
    unittest.main()
