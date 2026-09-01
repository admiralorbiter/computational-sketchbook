import pytest
from datetime import datetime, timedelta
from app.domains.health.models import Med, MedEvent, SymptomLog, Vital, Appointment
from app.domains.health.services import HealthService
from unittest.mock import Mock

class TestHealthModels:
    """Test health domain models"""
    
    def test_med_model(self):
        """Test medication model creation and serialization"""
        med = Med(
            name="Test Medication",
            dose_text="1 tablet daily",
            notes="Take with food"
        )
        
        assert med.name == "Test Medication"
        assert med.dose_text == "1 tablet daily"
        assert med.notes == "Take with food"
        
        # Test to_dict method
        med_dict = med.to_dict()
        assert med_dict['name'] == "Test Medication"
        assert med_dict['dose_text'] == "1 tablet daily"
        assert 'adherence_pct' in med_dict
    
    def test_med_event_model(self):
        """Test medication event model"""
        event = MedEvent(
            med_id=1,
            amount=1.0,
            note="Taken as prescribed"
        )
        
        assert event.med_id == 1
        assert event.amount == 1.0
        assert event.note == "Taken as prescribed"
        
        event_dict = event.to_dict()
        assert event_dict['med_id'] == 1
        assert event_dict['amount'] == 1.0
    
    def test_symptom_log_model(self):
        """Test symptom log model"""
        symptom = SymptomLog(
            label="Headache",
            severity=3,
            trigger="Stress",
            note="Moderate pain"
        )
        
        assert symptom.label == "Headache"
        assert symptom.severity == 3
        assert symptom.trigger == "Stress"
        
        symptom_dict = symptom.to_dict()
        assert symptom_dict['label'] == "Headache"
        assert symptom_dict['severity'] == 3
    
    def test_vital_model(self):
        """Test vital sign model"""
        vital = Vital(
            kind="BP",
            value_num=120.0,
            unit="mmHg",
            note="Systolic pressure"
        )
        
        assert vital.kind == "BP"
        assert vital.value_num == 120.0
        assert vital.unit == "mmHg"
        
        vital_dict = vital.to_dict()
        assert vital_dict['kind'] == "BP"
        assert vital_dict['value_num'] == 120.0
    
    def test_appointment_model(self):
        """Test appointment model"""
        appointment = Appointment(
            ts=datetime.now(),
            provider="Dr. Smith",
            location="Medical Center",
            purpose="Check-up",
            note="Annual physical"
        )
        
        assert appointment.provider == "Dr. Smith"
        assert appointment.location == "Medical Center"
        assert appointment.purpose == "Check-up"
        
        appointment_dict = appointment.to_dict()
        assert appointment_dict['provider'] == "Dr. Smith"

class TestHealthService:
    """Test health service layer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.service = HealthService(self.mock_db)
    
    def test_get_meds_empty(self):
        """Test getting medications when none exist"""
        self.mock_db.query.return_value.all.return_value = []
        
        meds = self.service.get_meds()
        
        assert meds == []
        self.mock_db.query.assert_called_once()
    
    def test_create_med(self):
        """Test creating a medication"""
        # Mock the database session
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None

        data = {
            'name': 'Test Med',
            'dose_text': '1 daily',
            'notes': 'Test notes'
        }

        result = self.service.create_med(data)

        # Check that the result is a Med object with correct data
        assert isinstance(result, Med)
        assert result.name == 'Test Med'
        assert result.dose_text == '1 daily'
        assert result.notes == 'Test notes'
        assert self.mock_db.add.called
        assert self.mock_db.commit.called
        assert self.mock_db.refresh.called
        # Note: add is called twice - once for med, once for audit
        assert self.mock_db.add.call_count == 2
        assert self.mock_db.commit.call_count == 2
    
    def test_log_med_event(self):
        """Test logging a medication event"""
        # Mock medication exists
        mock_med = Mock()
        mock_med.id = 1
        mock_med.name = "Test Med"
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_med
        
        # Mock event creation
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        result = self.service.log_med_event(1, 1.0, "Test note")
        
        # Check that the result is a MedEvent object with correct data
        assert isinstance(result, MedEvent)
        assert result.med_id == 1
        assert result.amount == 1.0
        assert result.note == "Test note"
        assert self.mock_db.add.called
        assert self.mock_db.commit.called
        assert self.mock_db.refresh.called
    
    def test_log_symptom(self):
        """Test logging a symptom"""
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        data = {
            'label': 'Headache',
            'severity': 3,
            'trigger': 'Stress',
            'note': 'Moderate pain'
        }
        
        result = self.service.log_symptom(data)
        
        # Check that the result is a SymptomLog object with correct data
        assert isinstance(result, SymptomLog)
        assert result.label == 'Headache'
        assert result.severity == 3
        assert result.trigger == 'Stress'
        assert result.note == 'Moderate pain'
        assert self.mock_db.add.called
        assert self.mock_db.commit.called
        assert self.mock_db.refresh.called
    
    def test_log_vital(self):
        """Test logging a vital sign"""
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        data = {
            'kind': 'BP',
            'value_num': 120.0,
            'unit': 'mmHg',
            'note': 'Systolic'
        }
        
        result = self.service.log_vital(data)
        
        # Check that the result is a Vital object with correct data
        assert isinstance(result, Vital)
        assert result.kind == 'BP'
        assert result.value_num == 120.0
        assert result.unit == 'mmHg'
        assert result.note == 'Systolic'
        assert self.mock_db.add.called
        assert self.mock_db.commit.called
        assert self.mock_db.refresh.called
    
    def test_create_appointment(self):
        """Test creating an appointment"""
        self.mock_db.add.return_value = None
        self.mock_db.commit.return_value = None
        self.mock_db.refresh.return_value = None
        
        data = {
            'ts': '2024-01-15T10:00:00',
            'provider': 'Dr. Smith',
            'location': 'Medical Center',
            'purpose': 'Check-up'
        }
        
        result = self.service.create_appointment(data)
        
        # Check that the result is an Appointment object with correct data
        assert isinstance(result, Appointment)
        assert result.provider == 'Dr. Smith'
        assert result.location == 'Medical Center'
        assert result.purpose == 'Check-up'
        assert self.mock_db.add.called
        assert self.mock_db.commit.called
        assert self.mock_db.refresh.called
    
    def test_get_dashboard_data(self):
        """Test getting dashboard data"""
        # Mock the service methods directly to return expected data
        self.service.get_meds = Mock(return_value=[])
        self.service.get_symptom_summary = Mock(return_value={'total': 0, 'by_severity': {}, 'by_label': {}, 'avg_severity': 0})
        self.service.get_vital_summary = Mock(return_value={'total': 0, 'by_kind': {}, 'recent': []})
        self.service.get_appointments = Mock(return_value=[])
        
        # Mock the private methods
        self.service._get_recent_med_events = Mock(return_value=[])
        self.service._get_next_appointment = Mock(return_value=None)

        result = self.service.get_dashboard_data()
        
        assert 'meds' in result
        assert 'symptoms' in result
        assert 'vitals' in result
        assert 'appointments' in result
        assert result['meds']['total'] == 0
        assert result['symptoms']['total'] == 0
        assert result['vitals']['total'] == 0
        assert result['appointments']['upcoming'] == 0
