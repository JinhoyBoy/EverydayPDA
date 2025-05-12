import unittest
from unittest.mock import AsyncMock, MagicMock
import asyncio
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from api.usecase_handler import UseCaseHandler, UseCases, UseCaseProcessor, DataFiller


class TestUseCaseHandler(unittest.TestCase):

    @unittest.mock.patch('api.usecase_handler.UseCaseProcessor')
    @unittest.mock.patch('api.usecase_handler.UseCases')
    @unittest.mock.patch('api.usecase_handler.DataFiller')
    def test_get_use_cases_and_info(self, MockDataFiller, MockUseCases, MockUseCaseProcessor):
        # Arrange
        mock_processor = MagicMock()
        mock_processor.declare_usecase.return_value = ['use_case_1', 'use_case_2']
        mock_processor.get_information.return_value = {'key1': 'value1'}

        MockUseCaseProcessor.return_value = mock_processor

        # Mock der asynchronen fill_missing_values Methode
        mock_data_filler = AsyncMock()
        mock_data_filler.fill_missing_values.return_value = {'key1': 'value1'}
        MockDataFiller.return_value = mock_data_filler

        mock_use_case = MagicMock()
        mock_use_case.information_needed = ['key1']
        mock_use_case.value = 'use_case_1'
        mock_use_case.name = 'Test UseCase'
        MockUseCases.__iter__.return_value = [mock_use_case]

        handler = UseCaseHandler()

        # Act
        use_cases, info = asyncio.run(handler.get_use_cases_and_info('some message', 'user123'))

        # Assert
        self.assertEqual(use_cases, ['use_case_1', 'use_case_2'])
        self.assertEqual(info, {'key1': 'value1'})
        mock_processor.declare_usecase.assert_called_once_with('some message')
        mock_processor.get_information.assert_called_once_with('some message', 'key1')
        mock_data_filler.fill_missing_values.assert_called_once_with({'key1': 'value1'}, 'user123')

    @unittest.mock.patch('api.usecase_handler.UseCases')
    def test_call_apis(self, MockUseCases):
        # Arrange
        mock_use_case = MagicMock()
        mock_use_case.information_needed = ['key1']
        mock_use_case.func.return_value = 'some_result'
        mock_use_case.description = 'Test UseCase Description'
        MockUseCases.return_value = mock_use_case

        handler = UseCaseHandler()

        # Act
        results = handler.call_apis(['use_case_1'], {'key1': 'value1'})

        # Assert
        self.assertEqual(results, {'Test UseCase Description': 'some_result'})
        mock_use_case.func.assert_called_once_with('value1')

    @unittest.mock.patch('api.usecase_handler.UseCaseProcessor')
    def test_get_response(self, MockUseCaseProcessor):
        # Arrange
        mock_processor = MagicMock()
        mock_processor.response.return_value = 'some_response'
        MockUseCaseProcessor.return_value = mock_processor

        handler = UseCaseHandler()

        # Act
        response = handler.get_response('some message', {'key': 'value'})

        # Assert
        self.assertEqual(response, 'some_response')
        mock_processor.response.assert_called_once_with('some message', {'key': 'value'})


if __name__ == '__main__':
    unittest.main()
