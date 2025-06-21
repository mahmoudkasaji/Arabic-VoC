"""
Database tests for Arabic VoC platform
Testing PostgreSQL with Arabic optimization, encoding, and search functionality
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from models.auth import User, Organization
from models.survey import Survey, Question, Response
from utils.database_arabic import arabic_db_manager, init_arabic_database

class TestArabicDatabaseConfiguration:
    """Test Arabic database configuration and encoding"""
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection with Arabic support"""
        await init_arabic_database()
        assert arabic_db_manager.engine is not None
        assert arabic_db_manager.session_factory is not None
    
    @pytest.mark.asyncio
    async def test_utf8_encoding(self):
        """Test UTF-8 encoding for Arabic characters"""
        async with arabic_db_manager.session_factory() as session:
            # Test Arabic text storage and retrieval
            arabic_text = "اختبار الترميز العربي مع الأرقام ١٢٣٤٥"
            
            result = await session.execute(
                text("SELECT :arabic_text as test_text"),
                {"arabic_text": arabic_text}
            )
            row = result.fetchone()
            
            assert row.test_text == arabic_text
            assert len(row.test_text) == len(arabic_text)
    
    @pytest.mark.asyncio
    async def test_arabic_normalization_function(self):
        """Test Arabic text normalization function"""
        async with arabic_db_manager.session_factory() as session:
            # Test normalization of Arabic text with diacritics
            text_with_diacritics = "مَرْحَبًا بِكُمْ"
            expected_normalized = "مرحبا بكم"
            
            result = await session.execute(
                text("SELECT normalize_arabic_text(:text) as normalized"),
                {"text": text_with_diacritics}
            )
            row = result.fetchone()
            
            # Check that diacritics are removed
            assert row.normalized != text_with_diacritics
            assert len(row.normalized) < len(text_with_diacritics)
    
    @pytest.mark.asyncio
    async def test_arabic_text_search_function(self):
        """Test Arabic full-text search function"""
        async with arabic_db_manager.session_factory() as session:
            # Test Arabic text search vector creation
            arabic_text = "منصة صوت العميل العربية"
            
            result = await session.execute(
                text("SELECT arabic_to_tsvector(:text) as search_vector"),
                {"text": arabic_text}
            )
            row = result.fetchone()
            
            assert row.search_vector is not None
            assert str(row.search_vector) != ""

class TestArabicUserModel:
    """Test user model with Arabic name support"""
    
    @pytest.mark.asyncio
    async def test_create_user_with_arabic_names(self):
        """Test creating user with Arabic names"""
        async with arabic_db_manager.session_factory() as session:
            # Create organization first
            org = Organization(
                name="Test Organization",
                name_ar="منظمة اختبار",
                description_ar="وصف باللغة العربية"
            )
            session.add(org)
            await session.commit()
            await session.refresh(org)
            
            # Create user with Arabic names
            user = User(
                username="testuser_ar",
                email="test.arabic@example.com",
                password_hash="hashed_password",
                first_name="Ahmed",
                last_name="Ali",
                first_name_ar="أحمد",
                last_name_ar="علي",
                display_name_ar="أحمد علي",
                organization_id=org.id,
                language_preference="ar"
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            # Verify Arabic names are stored correctly
            assert user.first_name_ar == "أحمد"
            assert user.last_name_ar == "علي"
            assert user.display_name_ar == "أحمد علي"
            assert user.full_name == "أحمد علي"  # Should use Arabic names
            assert user.language_preference == "ar"
    
    @pytest.mark.asyncio
    async def test_arabic_name_search(self):
        """Test searching users by Arabic names"""
        async with arabic_db_manager.session_factory() as session:
            # Create test users with Arabic names
            users_data = [
                ("محمد", "أحمد", "محمد أحمد"),
                ("فاطمة", "الزهراء", "فاطمة الزهراء"),
                ("علي", "حسن", "علي حسن")
            ]
            
            for first_ar, last_ar, display_ar in users_data:
                user = User(
                    username=f"user_{first_ar}",
                    email=f"{first_ar}@example.com",
                    password_hash="hashed_password",
                    first_name_ar=first_ar,
                    last_name_ar=last_ar,
                    display_name_ar=display_ar
                )
                session.add(user)
            
            await session.commit()
            
            # Search for Arabic names using full-text search
            search_query = "محمد"
            result = await session.execute(
                text("""
                    SELECT id, first_name_ar, last_name_ar,
                           ts_rank(arabic_to_tsvector(coalesce(first_name_ar, '') || ' ' || coalesce(last_name_ar, '')), 
                                   arabic_to_tsvector(:query)) as rank
                    FROM users 
                    WHERE arabic_to_tsvector(coalesce(first_name_ar, '') || ' ' || coalesce(last_name_ar, '')) 
                          @@ arabic_to_tsvector(:query)
                    ORDER BY rank DESC
                """),
                {"query": search_query}
            )
            
            results = result.fetchall()
            assert len(results) >= 1
            
            # First result should be the most relevant
            top_result = results[0]
            assert "محمد" in top_result.first_name_ar or "محمد" in top_result.last_name_ar
    
    @pytest.mark.asyncio
    async def test_user_display_properties(self):
        """Test user display properties in Arabic"""
        async with arabic_db_manager.session_factory() as session:
            # Test user with Arabic preference
            user_ar = User(
                username="arabic_user",
                email="arabic@example.com",
                password_hash="hashed_password",
                first_name="John",
                last_name="Doe",
                first_name_ar="يوحنا",
                last_name_ar="دو",
                display_name_ar="يوحنا دو",
                language_preference="ar"
            )
            session.add(user_ar)
            
            # Test user with English preference
            user_en = User(
                username="english_user",
                email="english@example.com",
                password_hash="hashed_password",
                first_name="Jane",
                last_name="Smith",
                first_name_ar="جين",
                last_name_ar="سميث",
                language_preference="en"
            )
            session.add(user_en)
            
            await session.commit()
            
            # Test Arabic user properties
            assert user_ar.full_name == "يوحنا دو"
            assert user_ar.display_name == "يوحنا دو"
            
            # Test English user properties
            assert user_en.full_name == "Jane Smith"
            assert user_en.display_name == "Jane Smith"

class TestArabicSurveyModel:
    """Test survey model with bilingual support"""
    
    @pytest.mark.asyncio
    async def test_create_bilingual_survey(self):
        """Test creating survey with Arabic and English content"""
        async with arabic_db_manager.session_factory() as session:
            # Create organization and user first
            org = Organization(name="Test Org", name_ar="منظمة اختبار")
            session.add(org)
            await session.commit()
            await session.refresh(org)
            
            user = User(
                username="creator",
                email="creator@example.com",
                password_hash="hashed_password",
                organization_id=org.id
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            # Create bilingual survey
            survey = Survey(
                title="Customer Satisfaction Survey",
                title_ar="استطلاع رضا العملاء",
                description="Please rate our services",
                description_ar="يرجى تقييم خدماتنا",
                primary_language="ar",
                supported_languages=["ar", "en"],
                welcome_message="Welcome to our survey",
                welcome_message_ar="مرحباً بكم في استطلاعنا",
                organization_id=org.id,
                created_by=user.id,
                rtl_enabled=True
            )
            
            session.add(survey)
            await session.commit()
            await session.refresh(survey)
            
            # Verify bilingual content
            assert survey.title_ar == "استطلاع رضا العملاء"
            assert survey.description_ar == "يرجى تقييم خدماتنا"
            assert survey.display_title == "استطلاع رضا العملاء"  # Should use Arabic
            assert survey.primary_language == "ar"
            assert survey.rtl_enabled is True
    
    @pytest.mark.asyncio
    async def test_arabic_survey_search(self):
        """Test searching surveys by Arabic content"""
        async with arabic_db_manager.session_factory() as session:
            # Create test surveys with Arabic content
            surveys_data = [
                ("استطلاع الرضا", "استطلاع لقياس رضا العملاء"),
                ("تقييم الخدمات", "تقييم جودة الخدمات المقدمة"),
                ("آراء العملاء", "جمع آراء العملاء حول المنتجات")
            ]
            
            # Create organization and user
            org = Organization(name="Test Org")
            session.add(org)
            await session.commit()
            await session.refresh(org)
            
            user = User(
                username="survey_creator",
                email="creator@example.com",
                password_hash="hashed_password",
                organization_id=org.id
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            for title_ar, desc_ar in surveys_data:
                survey = Survey(
                    title=f"Survey {title_ar}",
                    title_ar=title_ar,
                    description_ar=desc_ar,
                    organization_id=org.id,
                    created_by=user.id
                )
                session.add(survey)
            
            await session.commit()
            
            # Search for surveys with Arabic keywords
            search_query = "رضا"
            result = await session.execute(
                text("""
                    SELECT id, title_ar, description_ar,
                           ts_rank(arabic_to_tsvector(coalesce(title_ar, '') || ' ' || coalesce(description_ar, '')), 
                                   arabic_to_tsvector(:query)) as rank
                    FROM surveys 
                    WHERE arabic_to_tsvector(coalesce(title_ar, '') || ' ' || coalesce(description_ar, '')) 
                          @@ arabic_to_tsvector(:query)
                    ORDER BY rank DESC
                """),
                {"query": search_query}
            )
            
            results = result.fetchall()
            assert len(results) >= 1
            
            # Verify results contain the search term
            for row in results:
                assert "رضا" in row.title_ar or "رضا" in row.description_ar

class TestArabicQuestionResponse:
    """Test question and response models with Arabic content"""
    
    @pytest.mark.asyncio
    async def test_arabic_question_creation(self):
        """Test creating questions with Arabic text"""
        async with arabic_db_manager.session_factory() as session:
            # Create survey first
            org = Organization(name="Test Org")
            session.add(org)
            await session.commit()
            await session.refresh(org)
            
            user = User(
                username="creator",
                email="creator@example.com",
                password_hash="hashed_password",
                organization_id=org.id
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            survey = Survey(
                title="Test Survey",
                organization_id=org.id,
                created_by=user.id
            )
            session.add(survey)
            await session.commit()
            await session.refresh(survey)
            
            # Create question with Arabic text
            question = Question(
                survey_id=survey.id,
                text="How would you rate our service?",
                text_ar="كيف تقيم خدماتنا؟",
                description="Please provide your rating",
                description_ar="يرجى تقديم تقييمكم",
                type="rating",
                rtl_enabled=True,
                min_value=1,
                max_value=5,
                options={"labels_ar": ["سيء جداً", "سيء", "متوسط", "جيد", "ممتاز"]}
            )
            
            session.add(question)
            await session.commit()
            await session.refresh(question)
            
            # Verify Arabic question content
            assert question.text_ar == "كيف تقيم خدماتنا؟"
            assert question.description_ar == "يرجى تقديم تقييمكم"
            assert question.rtl_enabled is True
            assert question.options["labels_ar"] is not None
    
    @pytest.mark.asyncio
    async def test_arabic_response_storage(self):
        """Test storing responses with Arabic content"""
        async with arabic_db_manager.session_factory() as session:
            # Create survey structure
            org = Organization(name="Test Org")
            session.add(org)
            await session.commit()
            await session.refresh(org)
            
            user = User(
                username="creator",
                email="creator@example.com",
                password_hash="hashed_password",
                organization_id=org.id
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            survey = Survey(
                title="Test Survey",
                organization_id=org.id,
                created_by=user.id
            )
            session.add(survey)
            await session.commit()
            await session.refresh(survey)
            
            # Create response with Arabic content
            arabic_answers = {
                "1": {
                    "question": "ما رأيك في خدماتنا؟",
                    "answer": "الخدمة ممتازة وأنصح بها بشدة",
                    "type": "text"
                },
                "2": {
                    "question": "تقييم الجودة",
                    "answer": 5,
                    "type": "rating"
                }
            }
            
            response = Response(
                survey_id=survey.id,
                respondent_name="Ahmed Ali",
                respondent_name_ar="أحمد علي",
                answers=arabic_answers,
                language_used="ar",
                is_complete=True,
                sentiment_score=0.8,
                keywords=["ممتازة", "أنصح", "جودة"]
            )
            
            session.add(response)
            await session.commit()
            await session.refresh(response)
            
            # Verify Arabic response storage
            assert response.respondent_name_ar == "أحمد علي"
            assert response.language_used == "ar"
            assert response.answers["1"]["answer"] == "الخدمة ممتازة وأنصح بها بشدة"
            assert response.keywords == ["ممتازة", "أنصح", "جودة"]
    
    @pytest.mark.asyncio
    async def test_jsonb_arabic_search(self):
        """Test JSONB search with Arabic content"""
        async with arabic_db_manager.session_factory() as session:
            # Create survey and responses with Arabic content
            org = Organization(name="Test Org")
            session.add(org)
            await session.commit()
            await session.refresh(org)
            
            user = User(
                username="creator",
                email="creator@example.com",
                password_hash="hashed_password",
                organization_id=org.id
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            survey = Survey(
                title="Test Survey",
                organization_id=org.id,
                created_by=user.id
            )
            session.add(survey)
            await session.commit()
            await session.refresh(survey)
            
            # Create responses with different Arabic content
            responses_data = [
                {"comment": "الخدمة ممتازة جداً"},
                {"comment": "المنتج جيد ولكن يحتاج تحسين"},
                {"comment": "تجربة سيئة ولا أنصح بها"}
            ]
            
            for i, answer_data in enumerate(responses_data):
                response = Response(
                    survey_id=survey.id,
                    answers={f"comment_{i}": answer_data},
                    language_used="ar"
                )
                session.add(response)
            
            await session.commit()
            
            # Search for responses containing specific Arabic words
            search_word = "ممتازة"
            result = await session.execute(
                text("""
                    SELECT id, answers
                    FROM responses 
                    WHERE answers::text LIKE :search_pattern
                """),
                {"search_pattern": f"%{search_word}%"}
            )
            
            results = result.fetchall()
            assert len(results) >= 1
            
            # Verify search results contain the Arabic word
            for row in results:
                assert search_word in str(row.answers)

class TestDatabasePerformance:
    """Test database performance with Arabic content"""
    
    @pytest.mark.asyncio
    async def test_arabic_index_performance(self):
        """Test performance of Arabic text indexes"""
        async with arabic_db_manager.session_factory() as session:
            # Test that indexes exist
            result = await session.execute(
                text("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename IN ('users', 'surveys', 'questions', 'responses')
                    AND indexname LIKE '%arabic%'
                """)
            )
            
            indexes = result.fetchall()
            index_names = [row.indexname for row in indexes]
            
            # Verify Arabic-specific indexes exist
            expected_indexes = [
                'idx_users_arabic_names_gin',
                'idx_organizations_arabic_name_gin',
                'idx_surveys_arabic_content_gin',
                'idx_questions_arabic_text_gin'
            ]
            
            for expected_index in expected_indexes:
                assert expected_index in index_names
    
    @pytest.mark.asyncio
    async def test_query_plan_optimization(self):
        """Test that Arabic queries use indexes efficiently"""
        async with arabic_db_manager.session_factory() as session:
            # Test query plan for Arabic name search
            result = await session.execute(
                text("""
                    EXPLAIN (FORMAT JSON)
                    SELECT id, first_name_ar, last_name_ar
                    FROM users 
                    WHERE arabic_to_tsvector(coalesce(first_name_ar, '') || ' ' || coalesce(last_name_ar, '')) 
                          @@ arabic_to_tsvector('محمد')
                """)
            )
            
            plan = result.fetchone()[0]
            
            # Verify that the query plan uses indexes (not sequential scan)
            plan_str = str(plan)
            assert "Seq Scan" not in plan_str or "Index" in plan_str
    
    @pytest.mark.asyncio
    async def test_bulk_arabic_insert_performance(self):
        """Test performance of bulk Arabic data insertion"""
        import time
        
        async with arabic_db_manager.session_factory() as session:
            # Create organization first
            org = Organization(name="Bulk Test Org")
            session.add(org)
            await session.commit()
            await session.refresh(org)
            
            # Measure time for bulk Arabic user insertion
            start_time = time.time()
            
            arabic_names = [
                ("محمد", "أحمد"), ("فاطمة", "الزهراء"), ("علي", "حسن"),
                ("عائشة", "الصديقة"), ("حسن", "العسكري"), ("زينب", "الحوراء")
            ]
            
            users = []
            for i, (first_ar, last_ar) in enumerate(arabic_names * 10):  # 60 users
                user = User(
                    username=f"bulk_user_{i}",
                    email=f"bulk_user_{i}@example.com",
                    password_hash="hashed_password",
                    first_name_ar=first_ar,
                    last_name_ar=last_ar,
                    organization_id=org.id
                )
                users.append(user)
            
            session.add_all(users)
            await session.commit()
            
            end_time = time.time()
            insert_time = end_time - start_time
            
            # Should complete within reasonable time (less than 5 seconds for 60 users)
            assert insert_time < 5.0
            
            # Verify all users were inserted
            result = await session.execute(
                text("SELECT COUNT(*) FROM users WHERE username LIKE 'bulk_user_%'")
            )
            count = result.scalar()
            assert count == 60