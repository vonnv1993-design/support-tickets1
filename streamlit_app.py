import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64
from typing import Dict, List
import json
import requests
import uuid

# [Giữ nguyên các import và config từ file cũ...]

# Thêm vào session state initialization
if 'market_research' not in st.session_state:
    st.session_state.market_research = {}
if 'software_database' not in st.session_state:
    # Database mẫu các phần mềm thị trường
    st.session_state.software_database = {
        'ERP': [
            {
                'name': 'SAP S/4HANA',
                'vendor': 'SAP SE',
                'category': 'ERP',
                'price_range': '50,000-500,000 USD',
                'deployment': ['On-premise', 'Cloud', 'Hybrid'],
                'features': ['Financial Management', 'Supply Chain', 'Manufacturing', 'HR'],
                'pros': ['Comprehensive functionality', 'Strong integration', 'Industry-specific solutions'],
                'cons': ['High cost', 'Complex implementation', 'Steep learning curve'],
                'rating': 4.2,
                'market_share': '22%',
                'website': 'https://www.sap.com',
                'support_vietnam': True
            },
            {
                'name': 'Oracle NetSuite',
                'vendor': 'Oracle Corporation',
                'category': 'ERP',
                'price_range': '99-499 USD/user/month',
                'deployment': ['Cloud'],
                'features': ['Financials', 'CRM', 'E-commerce', 'Inventory'],
                'pros': ['Cloud-native', 'Scalable', 'Good for SMEs'],
                'cons': ['Limited customization', 'Can be expensive', 'Learning curve'],
                'rating': 4.1,
                'market_share': '15%',
                'website': 'https://www.netsuite.com',
                'support_vietnam': True
            }
        ],
        'CRM': [
            {
                'name': 'Salesforce Sales Cloud',
                'vendor': 'Salesforce',
                'category': 'CRM',
                'price_range': '25-300 USD/user/month',
                'deployment': ['Cloud'],
                'features': ['Lead Management', 'Opportunity Management', 'Sales Analytics', 'Mobile App'],
                'pros': ['Market leader', 'Extensive customization', 'Strong ecosystem'],
                'cons': ['Expensive', 'Complex for small businesses', 'Requires training'],
                'rating': 4.3,
                'market_share': '23%',
                'website': 'https://www.salesforce.com',
                'support_vietnam': True
            },
            {
                'name': 'HubSpot CRM',
                'vendor': 'HubSpot',
                'category': 'CRM',
                'price_range': 'Free - 1,200 USD/month',
                'deployment': ['Cloud'],
                'features': ['Contact Management', 'Deal Pipeline', 'Email Marketing', 'Reports'],
                'pros': ['Free tier available', 'User-friendly', 'Good integration'],
                'cons': ['Limited advanced features in free tier', 'Can get expensive'],
                'rating': 4.5,
                'market_share': '12%',
                'website': 'https://www.hubspot.com',
                'support_vietnam': False
            }
        ],
        'HR': [
            {
                'name': 'Workday HCM',
                'vendor': 'Workday',
                'category': 'HR',
                'price_range': '100-300 USD/employee/year',
                'deployment': ['Cloud'],
                'features': ['Core HR', 'Payroll', 'Talent Management', 'Analytics'],
                'pros': ['Modern UI', 'Mobile-first', 'Strong analytics'],
                'cons': ['Expensive', 'Limited customization', 'Implementation complexity'],
                'rating': 4.0,
                'market_share': '18%',
                'website': 'https://www.workday.com',
                'support_vietnam': False
            }
        ]
    }

def market_research_page():
    st.header("🔍 THAM KHẢO PHẦN MẀM THỊ TRƯỜNG")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Khảo sát Thị trường", 
        "📊 So sánh Phần mềm", 
        "💡 AI Tư vấn", 
        "📋 Báo cáo Phân tích",
        "⚙️ Quản lý Database"
    ])
    
    with tab1:
        market_survey_section()
    
    with tab2:
        software_comparison_section()
    
    with tab3:
        ai_consultation_section()
    
    with tab4:
        market_analysis_report()
    
    with tab5:
        database_management_section()

def market_survey_section():
    st.subheader("🔍 KHẢO SÁT THỊ TRƯỜNG PHẦN MỀM")
    
    # Survey creation
    with st.expander("➕ Tạo Khảo sát Mới", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            survey_name = st.text_input("Tên khảo sát", placeholder="Ví dụ: Khảo sát ERP cho doanh nghiệp vừa")
            software_category = st.selectbox("Loại phần mềm", 
                                           ['ERP', 'CRM', 'HR', 'Accounting', 'Project Management', 'BI/Analytics', 'Other'])
            budget_range = st.selectbox("Ngân sách", 
                                      ['< 100 triệu VNĐ', '100-500 triệu VNĐ', '500 triệu - 2 tỷ VNĐ', '> 2 tỷ VNĐ'])
        
        with col2:
            company_size = st.selectbox("Quy mô công ty", 
                                      ['< 50 nhân viên', '50-200 nhân viên', '200-1000 nhân viên', '> 1000 nhân viên'])
            deployment_preference = st.multiselect("Hình thức triển khai ưu tiên",
                                                 ['On-premise', 'Cloud', 'Hybrid'])
            priority_features = st.multiselect("Tính năng ưu tiên",
                                             ['Cost-effective', 'Easy to use', 'Scalability', 'Integration', 
                                              'Security', 'Mobile support', 'Local support', 'Customization'])
        
        requirements = st.text_area("Yêu cầu chi tiết",
                                  placeholder="Mô tả chi tiết về yêu cầu nghiệp vụ, tính năng cần thiết...")
        
        if st.button("🚀 Tạo Khảo sát", type="primary"):
            if survey_name and software_category:
                survey_id = generate_id()
                st.session_state.market_research[survey_id] = {
                    'name': survey_name,
                    'category': software_category,
                    'budget_range': budget_range,
                    'company_size': company_size,
                    'deployment_preference': deployment_preference,
                    'priority_features': priority_features,
                    'requirements': requirements,
                    'created_date': datetime.now().isoformat(),
                    'status': 'Active',
                    'research_results': []
                }
                st.success(f"✅ Khảo sát '{survey_name}' đã được tạo thành công!")
                st.rerun()
    
    # Display existing surveys
    if st.session_state.market_research:
        st.subheader("📋 Danh sách Khảo sát")
        
        for survey_id, survey in st.session_state.market_research.items():
            with st.expander(f"📊 {survey['name']} - {survey['category']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Ngân sách:** {survey['budget_range']}")
                    st.write(f"**Quy mô:** {survey['company_size']}")
                
                with col2:
                    st.write(f"**Triển khai:** {', '.join(survey['deployment_preference'])}")
                    st.write(f"**Trạng thái:** {survey['status']}")
                
                with col3:
                    st.write(f"**Ngày tạo:** {survey['created_date'][:10]}")
                    st.write(f"**Kết quả:** {len(survey.get('research_results', []))} phần mềm")
                
                if st.button(f"🔍 Tìm kiếm Phần mềm", key=f"search_{survey_id}"):
                    # Auto search based on survey criteria
                    results = search_software_by_criteria(survey)
                    survey['research_results'] = results
                    st.success(f"✅ Đã tìm thấy {len(results)} phần mềm phù hợp!")
                    st.rerun()

def search_software_by_criteria(survey):
    """Search software based on survey criteria"""
    results = []
    category = survey['category']
    
    if category in st.session_state.software_database:
        for software in st.session_state.software_database[category]:
            # Simple matching logic - in production, this would be more sophisticated
            match_score = 0
            
            # Check deployment preference
            if any(dep in software['deployment'] for dep in survey['deployment_preference']):
                match_score += 30
            
            # Check support in Vietnam
            if 'Local support' in survey['priority_features'] and software['support_vietnam']:
                match_score += 20
            
            # Add to results with score
            software_result = software.copy()
            software_result['match_score'] = match_score
            software_result['survey_id'] = survey.get('survey_id', '')
            results.append(software_result)
    
    # Sort by match score
    return sorted(results, key=lambda x: x['match_score'], reverse=True)

def software_comparison_section():
    st.subheader("📊 SO SÁNH PHẦN MỀM")
    
    # Software selection for comparison
    all_software = []
    for category, software_list in st.session_state.software_database.items():
        all_software.extend(software_list)
    
    if not all_software:
        st.info("📝 Chưa có dữ liệu phần mềm để so sánh")
        return
    
    software_names = [sw['name'] for sw in all_software]
    selected_software = st.multiselect("Chọn phần mềm để so sánh (tối đa 4):", 
                                     software_names, max_selections=4)
    
    if len(selected_software) >= 2:
        # Get selected software data
        comparison_data = []
        for name in selected_software:
            for sw in all_software:
                if sw['name'] == name:
                    comparison_data.append(sw)
                    break
        
        # Comparison table
        st.subheader("📋 Bảng So sánh Chi tiết")
        
        comparison_df_data = {
            'Tiêu chí': ['Tên sản phẩm', 'Nhà cung cấp', 'Loại', 'Giá', 'Triển khai', 
                        'Đánh giá', 'Thị phần', 'Hỗ trợ VN', 'Website']
        }
        
        for sw in comparison_data:
            comparison_df_data[sw['name']] = [
                sw['name'],
                sw['vendor'],
                sw['category'],
                sw['price_range'],
                ', '.join(sw['deployment']),
                f"{sw['rating']}/5.0",
                sw['market_share'],
                '✅' if sw['support_vietnam'] else '❌',
                sw['website']
            ]
        
        comparison_df = pd.DataFrame(comparison_df_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Rating comparison
            fig_rating = go.Figure(data=[
                go.Bar(name='Rating', 
                      x=[sw['name'] for sw in comparison_data],
                      y=[sw['rating'] for sw in comparison_data])
            ])
            fig_rating.update_layout(title='So sánh Đánh giá (Rating)')
            st.plotly_chart(fig_rating, use_container_width=True)
        
        with col2:
            # Market share comparison
            fig_market = px.pie(
                values=[float(sw['market_share'].replace('%', '')) for sw in comparison_data],
                names=[sw['name'] for sw in comparison_data],
                title='Thị phần'
            )
            st.plotly_chart(fig_market, use_container_width=True)
        
        # Detailed feature comparison
        st.subheader("🔍 So sánh Tính năng Chi tiết")
        
        for i, sw in enumerate(comparison_data):
            with st.expander(f"📦 {sw['name']} - Chi tiết"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Ưu điểm:**")
                    for pro in sw['pros']:
                        st.write(f"✅ {pro}")
                    
                    st.write("**Tính năng chính:**")
                    for feature in sw['features']:
                        st.write(f"🔧 {feature}")
                
                with col2:
                    st.write("**Nhược điểm:**")
                    for con in sw['cons']:
                        st.write(f"❌ {con}")
        
        # Export comparison
        if st.button("📤 Xuất báo cáo so sánh"):
            st.markdown(create_download_link(comparison_df, 
                       f"software_comparison_{datetime.now().strftime('%Y%m%d')}.csv", 
                       "📥 Tải báo cáo so sánh"), unsafe_allow_html=True)

def ai_consultation_section():
    st.subheader("💡 AI TƯ VẤN CHỌN PHẦN MỀM")
    
    # AI Consultation Form
    with st.form("ai_consultation"):
        st.write("**Mô tả yêu cầu của bạn để AI tư vấn phần mềm phù hợp:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            business_type = st.selectbox("Loại hình kinh doanh",
                                       ['Sản xuất', 'Thương mại', 'Dịch vụ', 'Công nghệ', 'Tài chính', 'Y tế', 'Giáo dục'])
            current_pain_points = st.text_area("Vấn đề hiện tại đang gặp phải",
                                             placeholder="Ví dụ: Quản lý kho không hiệu quả, báo cáo tài chính chậm...")
        
        with col2:
            integration_needs = st.text_area("Yêu cầu tích hợp",
                                           placeholder="Ví dụ: Cần tích hợp với hệ thống kế toán hiện tại...")
            special_requirements = st.text_area("Yêu cầu đặc biệt",
                                              placeholder="Ví dụ: Phải tuân thủ quy định về dữ liệu cá nhân...")
        
        submitted = st.form_submit_button("🤖 Nhận Tư vấn AI", type="primary")
        
        if submitted:
            with st.spinner("🤖 AI đang phân tích yêu cầu của bạn..."):
                # Simulate AI analysis
                import time
                time.sleep(2)
                
                ai_recommendation = generate_ai_recommendation(
                    business_type, current_pain_points, integration_needs, special_requirements
                )
                
                st.success("✅ AI đã hoàn thành phân tích!")
                
                # Display AI recommendations
                st.subheader("🎯 KHUYẾN NGHỊ TỪ AI")
                
                tab1, tab2, tab3 = st.tabs(["🏆 Top Khuyến nghị", "📊 Phân tích", "⚠️ Lưu ý"])
                
                with tab1:
                    for i, rec in enumerate(ai_recommendation['top_recommendations'], 1):
                        with st.container():
                            st.write(f"### {i}. {rec['name']}")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Độ phù hợp", f"{rec['match_score']}/100")
                            with col2:
                                st.metric("Đánh giá", f"{rec['rating']}/5.0")
                            with col3:
                                st.metric("Chi phí ước tính", rec['estimated_cost'])
                            
                            st.write(f"**Lý do khuyến nghị:** {rec['reason']}")
                            st.write("---")
                
                with tab2:
                    st.write(ai_recommendation['analysis'])
                
                with tab3:
                    st.write(ai_recommendation['considerations'])

def generate_ai_recommendation(business_type, pain_points, integration_needs, special_requirements):
    """Generate AI recommendation based on input - This would use actual AI/LLM in production"""
    
    # Mock AI recommendation logic
    recommendations = []
    
    # Simple rule-based recommendation for demo
    if 'kho' in pain_points.lower() or 'inventory' in pain_points.lower():
        recommendations.append({
            'name': 'SAP S/4HANA',
            'match_score': 85,
            'rating': 4.2,
            'estimated_cost': '2-5 tỷ VNĐ',
            'reason': 'Mạnh về quản lý chuỗi cung ứng và inventory, phù hợp với doanh nghiệp lớn'
        })
    
    if business_type == 'Thương mại':
        recommendations.append({
            'name': 'Oracle NetSuite',
            'match_score': 78,
            'rating': 4.1,
            'estimated_cost': '500 triệu - 2 tỷ VNĐ',
            'reason': 'Giải pháp cloud tốt cho doanh nghiệp thương mại, tích hợp e-commerce'
        })
    
    # Ensure we have at least some recommendations
    if not recommendations:
        recommendations = [
            {
                'name': 'HubSpot CRM',
                'match_score': 72,
                'rating': 4.5,
                'estimated_cost': '100-500 triệu VNĐ/năm',
                'reason': 'Phù hợp cho doanh nghiệp SME, dễ sử dụng và có tier miễn phí'
            }
        ]
    
    return {
        'top_recommendations': recommendations[:3],
        'analysis': f"""
        **Phân tích tình huống:**
        - Loại hình: {business_type}
        - Vấn đề chính: {pain_points}
        - Yêu cầu tích hợp: {integration_needs}
        
        **Đánh giá:**
        Dựa trên thông tin bạn cung cấp, AI khuyến nghị tập trung vào các giải pháp có khả năng tích hợp cao 
        và phù hợp với quy mô doanh nghiệp của bạn.
        """,
        'considerations': """
        **Những điểm cần lưu ý:**
        - Nên thực hiện POC (Proof of Concept) trước khi đầu tư lớn
        - Xem xét khả năng hỗ trợ và đào tạo người dùng
        - Đánh giá tổng chi phí sở hữu (TCO) trong 3-5 năm
        - Kiểm tra khả năng tuân thủ quy định pháp lý Việt Nam
        """
    }

def market_analysis_report():
    st.subheader("📋 BÁO CÁO PHÂN TÍCH THỊ TRƯỜNG")
    
    # Market overview
    st.write("### 📊 Tổng quan Thị trường")
    
    # Calculate market statistics
    total_software = sum(len(sw_list) for sw_list in st.session_state.software_database.values())
    categories = list(st.session_state.software_database.keys())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tổng số phần mềm", total_software)
    
    with col2:
        st.metric("Số danh mục", len(categories))
    
    with col3:
        vietnam_support = sum(
            sum(1 for sw in sw_list if sw['support_vietnam']) 
            for sw_list in st.session_state.software_database.values()
        )
        st.metric("Hỗ trợ VN", f"{vietnam_support}/{total_software}")
    
    with col4:
        avg_rating = sum(
            sum(sw['rating'] for sw in sw_list) / len(sw_list)
            for sw_list in st.session_state.software_database.values()
            if sw_list
        ) / len(categories) if categories else 0
        st.metric("Đánh giá TB", f"{avg_rating:.1f}/5.0")
    
    # Category breakdown
    st.write("### 📈 Phân tích theo Danh mục")
    
    category_data = []
    for category, sw_list in st.session_state.software_database.items():
        if sw_list:
            avg_rating = sum(sw['rating'] for sw in sw_list) / len(sw_list)
            vietnam_support_count = sum(1 for sw in sw_list if sw['support_vietnam'])
            vietnam_support_pct = (vietnam_support_count / len(sw_list)) * 100
            
            category_data.append({
                'Danh mục': category,
                'Số lượng': len(sw_list),
                'Đánh giá TB': round(avg_rating, 1),
                'Hỗ trợ VN (%)': round(vietnam_support_pct, 1)
            })
    
    if category_data:
        df_category = pd.DataFrame(category_data)
        st.dataframe(df_category, use_container_width=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(df_category, x='Danh mục', y='Số lượng', 
                         title='Số lượng Phần mềm theo Danh mục')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(df_category, x='Danh mục', y='Đánh giá TB', 
                         title='Đánh giá Trung bình theo Danh mục')
            st.plotly_chart(fig2, use_container_width=True)
    
    # Trend analysis
    st.write("### 📈 Phân tích Xu hướng")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Xu hướng Triển khai:**")
        deployment_count = {'Cloud': 0, 'On-premise': 0, 'Hybrid': 0}
        
        for sw_list in st.session_state.software_database.values():
            for sw in sw_list:
                for deployment in sw['deployment']:
                    deployment_count[deployment] += 1
        
        fig_deployment = px.pie(
            values=list(deployment_count.values()),
            names=list(deployment_count.keys()),
            title='Hình thức Triển khai'
        )
        st.plotly_chart(fig_deployment, use_container_width=True)
    
    with col2:
        st.write("**Top Features phổ biến:**")
        feature_count = {}
        
        for sw_list in st.session_state.software_database.values():
            for sw in sw_list:
                for feature in sw['features']:
                    feature_count[feature] = feature_count.get(feature, 0) + 1
        
        # Get top 10 features
        top_features = sorted(feature_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        if top_features:
            fig_features = px.bar(
                x=[item[1] for item in top_features],
                y=[item[0] for item in top_features],
                orientation='h',
                title='Top 10 Tính năng Phổ biến'
            )
            fig_features.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_features, use_container_width=True)
    
    # Export report
    if st.button("📤 Xuất Báo cáo Thị trường"):
        # Create comprehensive market report
        all_software_data = []
        
        for category, sw_list in st.session_state.software_database.items():
            for sw in sw_list:
                all_software_data.append({
                    'Tên': sw['name'],
                    'Nhà cung cấp': sw['vendor'],
                    'Danh mục': sw['category'],
                    'Giá': sw['price_range'],
                    'Triển khai': ', '.join(sw['deployment']),
                    'Đánh giá': sw['rating'],
                    'Thị phần': sw['market_share'],
                    'Hỗ trợ VN': sw['support_vietnam'],
                    'Website': sw['website'],
                    'Tính năng': ', '.join(sw['features'][:3])  # Top 3 features
                })
        
        df_market_report = pd.DataFrame(all_software_data)
        
        st.markdown(create_download_link(
            df_market_report, 
            f"market_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
            "📥 Tải Báo cáo Thị trường"
        ), unsafe_allow_html=True)

def database_management_section():
    st.subheader("⚙️ QUẢN LÝ DATABASE PHẦN MỀM")
    
    # Add new software
    with st.expander("➕ Thêm Phần mềm Mới"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Tên phần mềm")
            new_vendor = st.text_input("Nhà cung cấp")
            new_category = st.selectbox("Danh mục", 
                                      list(st.session_state.software_database.keys()) + ['Tạo mới'])
            if new_category == 'Tạo mới':
                new_category = st.text_input("Tên danh mục mới")
        
        with col2:
            new_price = st.text_input("Khoảng giá", placeholder="Ví dụ: 100-500 USD/month")
            new_deployment = st.multiselect("Hình thức triển khai", 
                                          ['Cloud', 'On-premise', 'Hybrid'])
            new_rating = st.slider("Đánh giá", 1.0, 5.0, 4.0, 0.1)
        
        new_features = st.text_input("Tính năng chính (phân cách bằng dấu phẩy)")
        new_pros = st.text_input("Ưu điểm (phân cách bằng dấu phẩy)")
        new_cons = st.text_input("Nhược điểm (phân cách bằng dấu phẩy)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            new_market_share = st.text_input("Thị phần", placeholder="Ví dụ: 15%")
        with col2:
            new_website = st.text_input("Website")
        with col3:
            new_support_vn = st.checkbox("Hỗ trợ tại Việt Nam")
        
        if st.button("➕ Thêm Phần mềm"):
            if new_name and new_vendor and new_category:
                new_software = {
                    'name': new_name,
                    'vendor': new_vendor,
                    'category': new_category,
                    'price_range': new_price,
                    'deployment': new_deployment,
                    'features': [f.strip() for f in new_features.split(',') if f.strip()],
                    'pros': [p.strip() for p in new_pros.split(',') if p.strip()],
                    'cons': [c.strip() for c in new_cons.split(',') if c.strip()],
                    'rating': new_rating,
                    'market_share': new_market_share,
                    'website': new_website,
                    'support_vietnam': new_support_vn
                }
                
                if new_category not in st.session_state.software_database:
                    st.session_state.software_database[new_category] = []
                
                st.session_state.software_database[new_category].append(new_software)
                st.success(f"✅ Đã thêm phần mềm '{new_name}' thành công!")
                st.rerun()
    
    # Manage existing software
    st.write("### 📋 Danh sách Phần mềm Hiện tại")
    
    for category, sw_list in st.session_state.software_database.items():
        with st.expander(f"📂 {category} ({len(sw_list)} phần mềm)"):
            for i, sw in enumerate(sw_list):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{sw['name']}** - {sw['vendor']}")
                    st.write(f"Đánh giá: {sw['rating']}/5.0 | Thị phần: {sw['market_share']}")
                
                with col2:
                    if st.button("✏️ Sửa", key=f"edit_{category}_{i}"):
                        st.info("Tính năng chỉnh sửa - Sẽ được phát triển")
                
                with col3:
                    if st.button("🗑️ Xóa", key=f"delete_{category}_{i}"):
                        st.session_state.software_database[category].pop(i)
                        st.success(f"✅ Đã xóa {sw['name']}")
                        st.rerun()
    
    # Import/Export data
    st.write("### 📤📥 Import/Export Dữ liệu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export current database
        if st.button("📤 Xuất Database"):
            all_data = []
            for category, sw_list in st.session_state.software_database.items():
                for sw in sw_list:
                    sw_export = sw.copy()
                    sw_export['features_str'] = ', '.join(sw['features'])
                    sw_export['pros_str'] = ', '.join(sw['pros'])
                    sw_export['cons_str'] = ', '.join(sw['cons'])
                    sw_export['deployment_str'] = ', '.join(sw['deployment'])
                    all_data.append(sw_export)
            
            if all_data:
                df_export = pd.DataFrame(all_data)
                st.markdown(create_download_link(
                    df_export, 
                    f"software_database_{datetime.now().strftime('%Y%m%d')}.csv",
                    "📥 Tải Database"
                ), unsafe_allow_html=True)
    
    with col2:
        # Import data
        uploaded_file = st.file_uploader("📥 Import Database CSV", type=['csv'])
        if uploaded_file:
            try:
                df_import = pd.read_csv(uploaded_file)
                if st.button("🔄 Import Dữ liệu"):
                    # Process import - simplified for demo
                    st.success("✅ Import thành công! (Demo)")
            except Exception as e:
                st.error(f"❌ Lỗi import: {str(e)}")

# Update main navigation to include market research
def main():
    st.title("🏢 HỆ THỐNG QUẢN LÝ KẾ HOẠCH MUA SẮM")
    st.markdown("---")

    # Sidebar navigation
    with st.sidebar:
        st.header("📋 MENU CHỨC NĂNG")
        page = st.radio(
            "Chọn chức năng:",
            [
                "🏠 Dashboard Tổng quan",
                "📄 Giai đoạn 1: RFI & Gửi NCC",
                "💰 Giai đoạn 2: Kế hoạch Ngân sách", 
                "📊 Business Use Case",
                "🎯 Master Plan",
                "🔍 Tham khảo Phần mềm Thị trường"  # New feature
            ]
        )

    # Route to different pages
    if page == "🏠 Dashboard Tổng quan":
        dashboard_page()
    elif page == "📄 Giai đoạn 1: RFI & Gửi NCC":
        rfi_page()
    elif page == "💰 Giai đoạn 2: Kế hoạch Ngân sách":
        budget_page()
    elif page == "📊 Business Use Case":
        business_case_page()
    elif page == "🎯 Master Plan":
        master_plan_page()
    elif page == "🔍 Tham khảo Phần mềm Thị trường":
        market_research_page()

if __name__ == "__main__":
    main()
