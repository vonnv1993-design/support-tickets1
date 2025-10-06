import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import base64
from typing import Dict, List
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import uuid

# Page config
st.set_page_config(
    page_title="Hệ thống Quản lý Kế hoạch Mua sắm",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'projects' not in st.session_state:
    st.session_state.projects = {}
if 'suppliers' not in st.session_state:
    st.session_state.suppliers = {
        'Phần mềm': ['Công ty TNHH ABC Software', 'VTI Solutions', 'FPT Software'],
        'Hạ tầng': ['Dell Technologies', 'HP Enterprise', 'Cisco Systems'],
        'Bảo mật': ['Kaspersky', 'McAfee', 'Symantec']
    }
if 'rfis' not in st.session_state:
    st.session_state.rfis = {}

# Helper functions
def generate_id():
    return str(uuid.uuid4())[:8]

def create_download_link(df, filename, text):
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def send_email_mock(recipients, subject, body, attachments=None):
    """Mock email function - in production, configure SMTP settings"""
    st.success(f"✅ Email đã được gửi tới {len(recipients)} nhà cung cấp")
    return True

# Main app
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
                "🎯 Master Plan"
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

def dashboard_page():
    st.header("📊 DASHBOARD TỔNG QUAN")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tổng số dự án", len(st.session_state.projects))
    
    with col2:
        rfis_sent = sum(1 for rfi in st.session_state.rfis.values() if rfi.get('status') == 'Đã gửi')
        st.metric("RFI đã gửi", rfis_sent)
    
    with col3:
        total_budget = sum(p.get('total_budget', 0) for p in st.session_state.projects.values())
        st.metric("Tổng ngân sách", f"{total_budget:,.0f} VNĐ")
    
    with col4:
        completed_projects = sum(1 for p in st.session_state.projects.values() 
                               if p.get('master_plan', {}).get('step_5', {}).get('status') == 'Hoàn thành')
        st.metric("Dự án hoàn thành", completed_projects)

    if st.session_state.projects:
        st.subheader("📈 Biểu đồ Tiến độ Dự án")
        
        # Create project status data
        project_data = []
        for proj_id, project in st.session_state.projects.items():
            master_plan = project.get('master_plan', {})
            completed_steps = sum(1 for step in master_plan.values() 
                                if step.get('status') == 'Hoàn thành')
            progress = (completed_steps / 5) * 100
            project_data.append({
                'Dự án': project.get('name', f'Dự án {proj_id}'),
                'Tiến độ (%)': progress,
                'Ngân sách (triệu VNĐ)': project.get('total_budget', 0) / 1000000
            })
        
        df_projects = pd.DataFrame(project_data)
        
        if not df_projects.empty:
            fig = px.bar(df_projects, x='Dự án', y='Tiến độ (%)', 
                        title='Tiến độ các Dự án',
                        color='Tiến độ (%)',
                        color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("📝 Chưa có dự án nào. Vui lòng tạo dự án mới ở các chức năng khác.")

def rfi_page():
    st.header("📄 GIAI ĐOẠN 1: SOẠN THẢO RFI & GỬI NCC")
    
    tab1, tab2, tab3 = st.tabs(["✏️ Tạo RFI mới", "📋 Quản lý RFI", "📊 Báo cáo RFI"])
    
    with tab1:
        st.subheader("Tạo Request for Information (RFI)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("Tên dự án")
            rfi_title = st.text_input("Tiêu đề RFI")
            supplier_category = st.selectbox("Chọn lĩnh vực NCC", 
                                           list(st.session_state.suppliers.keys()))
        
        with col2:
            deadline = st.date_input("Hạn phản hồi", 
                                   datetime.now() + timedelta(days=14))
            priority = st.selectbox("Độ ưu tiên", ["Thấp", "Trung bình", "Cao", "Khẩn cấp"])
        
        st.subheader("Nội dung RFI")
        rfi_content = st.text_area("Mô tả yêu cầu chi tiết", height=200,
                                  placeholder="Nhập mô tả chi tiết về yêu cầu, thông số kỹ thuật, tiêu chí đánh giá...")
        
        # File upload
        uploaded_file = st.file_uploader("Upload file RFI (Word/PDF)", 
                                       type=['docx', 'pdf', 'doc'])
        
        # Supplier selection
        st.subheader("Chọn Nhà cung cấp")
        selected_suppliers = st.multiselect(
            "Danh sách NCC nhận RFI:",
            st.session_state.suppliers[supplier_category],
            default=st.session_state.suppliers[supplier_category]
        )
        
        if st.button("🚀 Tạo và Gửi RFI", type="primary"):
            if project_name and rfi_title and rfi_content and selected_suppliers:
                rfi_id = generate_id()
                
                # Save RFI
                st.session_state.rfis[rfi_id] = {
                    'project_name': project_name,
                    'title': rfi_title,
                    'content': rfi_content,
                    'category': supplier_category,
                    'suppliers': selected_suppliers,
                    'deadline': deadline.isoformat(),
                    'priority': priority,
                    'status': 'Đã gửi',
                    'created_date': datetime.now().isoformat(),
                    'responses': {}
                }
                
                # Mock send email
                send_email_mock(selected_suppliers, f"RFI: {rfi_title}", rfi_content)
                
                st.success(f"✅ RFI đã được tạo và gửi tới {len(selected_suppliers)} nhà cung cấp!")
                st.rerun()
            else:
                st.error("⚠️ Vui lòng điền đầy đủ thông tin bắt buộc")
    
    with tab2:
        st.subheader("Danh sách RFI")
        
        if st.session_state.rfis:
            for rfi_id, rfi in st.session_state.rfis.items():
                with st.expander(f"📄 {rfi['title']} - {rfi['project_name']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Trạng thái:** {rfi['status']}")
                        st.write(f"**Ưu tiên:** {rfi['priority']}")
                    
                    with col2:
                        st.write(f"**Hạn phản hồi:** {rfi['deadline']}")
                        st.write(f"**Số NCC:** {len(rfi['suppliers'])}")
                    
                    with col3:
                        responses = len(rfi.get('responses', {}))
                        st.write(f"**Đã phản hồi:** {responses}/{len(rfi['suppliers'])}")
                    
                    st.write("**Nội dung:**")
                    st.write(rfi['content'])
                    
                    # Mock response tracking
                    if st.button(f"📝 Cập nhật phản hồi", key=f"update_{rfi_id}"):
                        st.info("Tính năng cập nhật phản hồi NCC - Sẽ được phát triển")
        else:
            st.info("📝 Chưa có RFI nào được tạo")
    
    with tab3:
        st.subheader("Báo cáo Tổng hợp RFI")
        
        if st.session_state.rfis:
            # Create summary data
            rfi_data = []
            for rfi_id, rfi in st.session_state.rfis.items():
                responses = len(rfi.get('responses', {}))
                total_suppliers = len(rfi['suppliers'])
                response_rate = (responses / total_suppliers * 100) if total_suppliers > 0 else 0
                
                rfi_data.append({
                    'RFI ID': rfi_id,
                    'Dự án': rfi['project_name'],
                    'Tiêu đề': rfi['title'],
                    'Lĩnh vực': rfi['category'],
                    'Tổng NCC': total_suppliers,
                    'Đã phản hồi': responses,
                    'Tỷ lệ phản hồi (%)': response_rate,
                    'Trạng thái': rfi['status'],
                    'Hạn chót': rfi['deadline']
                })
            
            df_rfi = pd.DataFrame(rfi_data)
            st.dataframe(df_rfi, use_container_width=True)
            
            # Download report
            st.markdown(create_download_link(df_rfi, "rfi_report.csv", "📥 Tải báo cáo RFI"), 
                       unsafe_allow_html=True)
        else:
            st.info("📝 Chưa có dữ liệu RFI để báo cáo")

def budget_page():
    st.header("💰 GIAI ĐOẠN 2: HOÀN THIỆN BẢNG KẾ HOẠCH NGÂN SÁCH")
    
    # Project selection
    project_name = st.selectbox("Chọn dự án", 
                               options=["Tạo dự án mới"] + [f"{p['name']}" for p in st.session_state.projects.values()],
                               key="budget_project")
    
    if project_name == "Tạo dự án mới":
        project_name = st.text_input("Tên dự án mới")
        if project_name:
            project_id = generate_id()
            st.session_state.projects[project_id] = {
                'name': project_name,
                'created_date': datetime.now().isoformat(),
                'budget_items': [],
                'total_budget': 0
            }
    
    if project_name and project_name != "Tạo dự án mới":
        # Find project
        current_project = None
        current_project_id = None
        for proj_id, project in st.session_state.projects.items():
            if project['name'] == project_name:
                current_project = project
                current_project_id = proj_id
                break
        
        if current_project:
            st.subheader(f"📊 Bảng Ngân sách - {project_name}")
            
            # Add budget item
            with st.expander("➕ Thêm hạng mục mới"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    item_name = st.text_input("Tên hạng mục")
                    authority_level = st.selectbox("Cấp thẩm quyền", 
                                                 ["Ban", "Phòng", "Tổng công ty", "HĐQT"])
                
                with col2:
                    unit_price = st.number_input("Đơn giá (VNĐ)", min_value=0, step=1000)
                    months = st.number_input("Số tháng", min_value=1, value=1)
                
                with col3:
                    vat_rate = st.number_input("Thuế VAT (%)", min_value=0, max_value=100, value=10)
                    notes = st.text_area("Ghi chú", height=80)
                
                if st.button("➕ Thêm hạng mục"):
                    if item_name and unit_price > 0:
                        before_tax = unit_price * months
                        after_tax = before_tax * (1 + vat_rate/100)
                        
                        budget_item = {
                            'name': item_name,
                            'authority_level': authority_level,
                            'unit_price': unit_price,
                            'months': months,
                            'before_tax': before_tax,
                            'after_tax': after_tax,
                            'vat_rate': vat_rate,
                            'notes': notes
                        }
                        
                        if 'budget_items' not in current_project:
                            current_project['budget_items'] = []
                        
                        current_project['budget_items'].append(budget_item)
                        current_project['total_budget'] = sum(item['after_tax'] for item in current_project['budget_items'])
                        
                        st.success("✅ Đã thêm hạng mục thành công!")
                        st.rerun()
                    else:
                        st.error("⚠️ Vui lòng điền đầy đủ thông tin")
            
            # Display budget table
            if current_project.get('budget_items'):
                budget_data = []
                for i, item in enumerate(current_project['budget_items'], 1):
                    budget_data.append({
                        'STT': i,
                        'Hạng mục': item['name'],
                        'Cấp thẩm quyền': item['authority_level'],
                        'Đơn giá (VNĐ)': f"{item['unit_price']:,.0f}",
                        'Số tháng': item['months'],
                        'Thành tiền (trước thuế)': f"{item['before_tax']:,.0f}",
                        'Sau thuế (VAT)': f"{item['after_tax']:,.0f}",
                        'Ghi chú': item['notes']
                    })
                
                df_budget = pd.DataFrame(budget_data)
                st.dataframe(df_budget, use_container_width=True)
                
                # Summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_before_tax = sum(item['before_tax'] for item in current_project['budget_items'])
                    st.metric("Tổng trước thuế", f"{total_before_tax:,.0f} VNĐ")
                
                with col2:
                    total_after_tax = sum(item['after_tax'] for item in current_project['budget_items'])
                    st.metric("Tổng sau thuế", f"{total_after_tax:,.0f} VNĐ")
                
                with col3:
                    avg_monthly = total_after_tax / 12 if total_after_tax > 0 else 0
                    st.metric("Chi phí TB/tháng", f"{avg_monthly:,.0f} VNĐ")
                
                # Budget approval warning
                if total_after_tax > 1000000000:  # 1 billion VND
                    st.warning("⚠️ Vượt ngưỡng phê duyệt cấp Ban (>1 tỷ VNĐ) - Cần trình Tổng công ty")
                elif total_after_tax > 500000000:  # 500 million VND
                    st.info("ℹ️ Vượt ngưỡng phê duyệt cấp Phòng (>500 triệu VNĐ) - Cần trình cấp Ban")
                
                # Export options
                st.markdown("### 📤 Xuất báo cáo")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(create_download_link(df_budget, f"budget_{project_name}.csv", 
                                                   "📥 Tải Excel"), unsafe_allow_html=True)
                with col2:
                    if st.button("📧 Gửi báo cáo"):
                        st.success("✅ Báo cáo đã được gửi!")
            
            else:
                st.info("📝 Chưa có hạng mục nào. Vui lòng thêm hạng mục mới.")

def business_case_page():
    st.header("📊 BUSINESS USE CASE CHO TỪNG DỰ ÁN")
    
    # Project selection
    if not st.session_state.projects:
        st.info("📝 Chưa có dự án nào. Vui lòng tạo dự án ở phần Kế hoạch Ngân sách.")
        return
    
    project_options = [p['name'] for p in st.session_state.projects.values()]
    selected_project = st.selectbox("Chọn dự án", project_options)
    
    if selected_project:
        # Find project
        current_project = None
        current_project_id = None
        for proj_id, project in st.session_state.projects.items():
            if project['name'] == selected_project:
                current_project = project
                current_project_id = proj_id
                break
        
        st.subheader(f"📋 Business Case - {selected_project}")
        
        # Initialize business case if not exists
        if 'business_case' not in current_project:
            current_project['business_case'] = {}
        
        tab1, tab2, tab3 = st.tabs(["🔍 Hiện trạng", "⚡ Sự cần thiết", "📈 Hiệu quả dự kiến"])
        
        with tab1:
            st.subheader("🔍 HIỆN TRẠNG")
            
            current_situation = st.text_area(
                "Mô tả vấn đề hoặc hạn chế hiện tại:",
                value=current_project['business_case'].get('current_situation', ''),
                height=150,
                placeholder="Ví dụ: Hệ thống hiện tại chậm, không đáp ứng được khối lượng công việc..."
            )
            
            current_challenges = st.text_area(
                "Các thách thức cụ thể:",
                value=current_project['business_case'].get('current_challenges', ''),
                height=150,
                placeholder="Liệt kê các thách thức, bottleneck, pain points..."
            )
            
            current_metrics = st.text_area(
                "Các chỉ số hiện tại (KPI):",
                value=current_project['business_case'].get('current_metrics', ''),
                height=100,
                placeholder="Thời gian xử lý, chi phí, độ hài lòng khách hàng..."
            )
            
            # Image upload for current state
            current_image = st.file_uploader("Upload hình ảnh minh họa hiện trạng", 
                                           type=['png', 'jpg', 'jpeg'], key="current_img")
        
        with tab2:
            st.subheader("⚡ SỰ CẦN THIẾT")
            
            business_requirements = st.text_area(
                "Yêu cầu nghiệp vụ:",
                value=current_project['business_case'].get('business_requirements', ''),
                height=150,
                placeholder="Mô tả yêu cầu từ nghiệp vụ, quy trình làm việc..."
            )
            
            strategic_alignment = st.text_area(
                "Căn cứ chiến lược chuyển đổi số:",
                value=current_project['business_case'].get('strategic_alignment', ''),
                height=150,
                placeholder="Liên kết với chiến lược công ty, chuyển đổi số, mục tiêu dài hạn..."
            )
            
            urgency_level = st.selectbox(
                "Mức độ cấp thiết:",
                ["Khẩn cấp", "Cao", "Trung bình", "Thấp"],
                index=["Khẩn cấp", "Cao", "Trung bình", "Thấp"].index(
                    current_project['business_case'].get('urgency_level', 'Trung bình')
                )
            )
            
            regulatory_compliance = st.text_area(
                "Yêu cầu tuân thủ (nếu có):",
                value=current_project['business_case'].get('regulatory_compliance', ''),
                height=100,
                placeholder="Các quy định pháp lý, chuẩn mực ngành..."
            )
        
        with tab3:
            st.subheader("📈 HIỆU QUẢ DỰ KIẾN")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Lợi ích định lượng:**")
                cost_saving = st.number_input(
                    "Tiết kiệm chi phí (VNĐ/năm):",
                    value=current_project['business_case'].get('cost_saving', 0),
                    step=1000000
                )
                
                time_saving = st.number_input(
                    "Tiết kiệm thời gian (giờ/tháng):",
                    value=current_project['business_case'].get('time_saving', 0),
                    step=1
                )
                
                productivity_increase = st.number_input(
                    "Tăng năng suất (%):",
                    value=current_project['business_case'].get('productivity_increase', 0),
                    step=5
                )
            
            with col2:
                st.write("**Lợi ích định tính:**")
                quality_improvement = st.text_area(
                    "Cải thiện chất lượng:",
                    value=current_project['business_case'].get('quality_improvement', ''),
                    height=80
                )
                
                user_experience = st.text_area(
                    "Trải nghiệm người dùng:",
                    value=current_project['business_case'].get('user_experience', ''),
                    height=80
                )
                
                process_improvement = st.text_area(
                    "Cải thiện quy trình:",
                    value=current_project['business_case'].get('process_improvement', ''),
                    height=80
                )
            
            # ROI calculation
            st.write("**Tính toán ROI:**")
            investment = current_project.get('total_budget', 0)
            annual_benefit = cost_saving + (time_saving * 12 * 200000)  # Assume 200k VND per hour
            
            if investment > 0:
                roi = (annual_benefit / investment * 100) if investment > 0 else 0
                payback_period = (investment / annual_benefit * 12) if annual_benefit > 0 else float('inf')
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("ROI (%)", f"{roi:.1f}%")
                with col2:
                    st.metric("Lợi ích/năm", f"{annual_benefit:,.0f} VNĐ")
                with col3:
                    if payback_period != float('inf'):
                        st.metric("Thời gian hoài vốn", f"{payback_period:.1f} tháng")
                    else:
                        st.metric("Thời gian hoài vốn", "N/A")
        
        # Save business case
        if st.button("💾 Lưu Business Case", type="primary"):
            current_project['business_case'].update({
                'current_situation': current_situation,
                'current_challenges': current_challenges,
                'current_metrics': current_metrics,
                'business_requirements': business_requirements,
                'strategic_alignment': strategic_alignment,
                'urgency_level': urgency_level,
                'regulatory_compliance': regulatory_compliance,
                'cost_saving': cost_saving,
                'time_saving': time_saving,
                'productivity_increase': productivity_increase,
                'quality_improvement': quality_improvement,
                'user_experience': user_experience,
                'process_improvement': process_improvement,
                'updated_date': datetime.now().isoformat()
            })
            
            st.success("✅ Business Case đã được lưu thành công!")
        
        # Export business case
        if st.button("📤 Xuất báo cáo Business Case"):
            # Create business case summary
            bc = current_project.get('business_case', {})
            summary_data = {
                'Thông tin': ['Dự án', 'Ngân sách', 'ROI (%)', 'Thời gian hoài vốn'],
                'Giá trị': [
                    selected_project,
                    f"{investment:,.0f} VNĐ",
                    f"{roi:.1f}%" if investment > 0 else "N/A",
                    f"{payback_period:.1f} tháng" if payback_period != float('inf') else "N/A"
                ]
            }
            
            df_summary = pd.DataFrame(summary_data)
            st.markdown(create_download_link(df_summary, f"business_case_{selected_project}.csv", 
                                           "📥 Tải Business Case"), unsafe_allow_html=True)

def master_plan_page():
    st.header("🎯 MASTER PLAN - QUẢN LÝ TOÀN TRÌNH TRIỂN KHAI")
    
    if not st.session_state.projects:
        st.info("📝 Chưa có dự án nào. Vui lòng tạo dự án ở phần Kế hoạch Ngân sách.")
        return
    
    # Project selection
    project_options = [p['name'] for p in st.session_state.projects.values()]
    selected_project = st.selectbox("Chọn dự án", project_options, key="master_plan_project")
    
    if selected_project:
        # Find project
        current_project = None
        current_project_id = None
        for proj_id, project in st.session_state.projects.items():
            if project['name'] == selected_project:
                current_project = project
                current_project_id = proj_id
                break
        
        st.subheader(f"📅 Master Plan - {selected_project}")
        
        # Initialize master plan if not exists
        if 'master_plan' not in current_project:
            current_project['master_plan'] = {}
        
        # Define the 5 steps
        steps = {
            'step_1': {
                'name': '1. Khảo sát & Hoàn thiện tờ trình',
                'description': 'Thu thập yêu cầu, soạn thảo đề xuất',
                'icon': '🔍'
            },
            'step_2': {
                'name': '2. Lựa chọn nhà cung cấp (LCNCC)',
                'description': 'RFI, so sánh, đàm phán, chọn NCC',
                'icon': '🏢'
            },
            'step_3': {
                'name': '3. Triển khai',
                'description': 'Ký hợp đồng, triển khai kỹ thuật',
                'icon': '⚙️'
            },
            'step_4': {
                'name': '4. Nghiệm thu',
                'description': 'Kiểm thử, nghiệm thu kỹ thuật & nghiệp vụ',
                'icon': '✅'
            },
            'step_5': {
                'name': '5. Đưa vào sử dụng',
                'description': 'Chuyển giao, đào tạo, đánh giá hiệu quả',
                'icon': '🚀'
            }
        }
        
        # Master Plan Progress
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Progress tracking
            completed_steps = 0
            total_steps = len(steps)
            
            for step_key, step_info in steps.items():
                if step_key not in current_project['master_plan']:
                    current_project['master_plan'][step_key] = {
                        'status': 'Chưa bắt đầu',
                        'assignee': '',
                        'deadline': '',
                        'notes': '',
                        'progress': 0
                    }
                
                step_data = current_project['master_plan'][step_key]
                if step_data['status'] == 'Hoàn thành':
                    completed_steps += 1
        
        with col2:
            progress_percentage = (completed_steps / total_steps) * 100
            st.metric("Tiến độ tổng thể", f"{progress_percentage:.0f}%")
            
            # Progress bar
            st.progress(progress_percentage / 100)
        
        # Step management
        st.subheader("📋 Chi tiết các Bước")
        
        for step_key, step_info in steps.items():
            step_data = current_project['master_plan'][step_key]
            
            with st.expander(f"{step_info['icon']} {step_info['name']}", 
                           expanded=(step_data['status'] not in ['Hoàn thành'])):
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status = st.selectbox(
                        "Trạng thái:",
                        ["Chưa bắt đầu", "Đang thực hiện", "Hoàn thành", "Tạm dừng"],
                        index=["Chưa bắt đầu", "Đang thực hiện", "Hoàn thành", "Tạm dừng"].index(step_data['status']),
                        key=f"{step_key}_status"
                    )
                
                with col2:
                    assignee = st.text_input(
                        "Người phụ trách:",
                        value=step_data['assignee'],
                        key=f"{step_key}_assignee"
                    )
                
                with col3:
                    deadline = st.date_input(
                        "Deadline:",
                        value=datetime.fromisoformat(step_data['deadline']) if step_data['deadline'] else datetime.now(),
                        key=f"{step_key}_deadline"
                    )
                
                progress = st.slider(
                    "Tiến độ (%)",
                    0, 100, 
                    value=step_data['progress'],
                    key=f"{step_key}_progress"
                )
                
                notes = st.text_area(
                    "Ghi chú:",
                    value=step_data['notes'],
                    height=80,
                    key=f"{step_key}_notes"
                )
                
                # Update step data
                current_project['master_plan'][step_key].update({
                    'status': status,
                    'assignee': assignee,
                    'deadline': deadline.isoformat(),
                    'progress': progress,
                    'notes': notes
                })
                
                # Status indicator
                if status == 'Hoàn thành':
                    st.success("✅ Bước này đã hoàn thành")
                elif status == 'Đang thực hiện':
                    if datetime.now().date() > deadline:
                        st.error("⚠️ Đã quá deadline!")
                    else:
                        days_left = (deadline - datetime.now().date()).days
                        st.info(f"🔄 Đang thực hiện - Còn {days_left} ngày")
                elif status == 'Tạm dừng':
                    st.warning("⏸️ Tạm dừng")
        
        # Save master plan
        if st.button("💾 Lưu Master Plan", type="primary"):
            current_project['master_plan']['updated_date'] = datetime.now().isoformat()
            st.success("✅ Master Plan đã được cập nhật!")
        
        # Master Plan Summary
        st.subheader("📊 Tóm tắt Master Plan")
        
        # Create summary table
        summary_data = []
        for step_key, step_info in steps.items():
            step_data = current_project['master_plan'][step_key]
            
            # Calculate days to deadline
            if step_data['deadline']:
                deadline_date = datetime.fromisoformat(step_data['deadline']).date()
                days_to_deadline = (deadline_date - datetime.now().date()).days
                if days_to_deadline < 0:
                    deadline_status = f"Quá hạn {abs(days_to_deadline)} ngày"
                elif days_to_deadline == 0:
                    deadline_status = "Hôm nay"
                else:
                    deadline_status = f"Còn {days_to_deadline} ngày"
            else:
                deadline_status = "Chưa set"
            
            summary_data.append({
                'Bước': step_info['name'],
                'Trạng thái': step_data['status'],
                'Người phụ trách': step_data['assignee'] or 'Chưa phân công',
                'Tiến độ (%)': f"{step_data['progress']}%",
                'Deadline': deadline_status,
                'Ghi chú': step_data['notes'][:50] + '...' if len(step_data['notes']) > 50 else step_data['notes']
            })
        
        df_master = pd.DataFrame(summary_data)
        st.dataframe(df_master, use_container_width=True)
        
        # Export master plan
        st.markdown(create_download_link(df_master, f"master_plan_{selected_project}.csv", 
                                       "📥 Tải Master Plan"), unsafe_allow_html=True)
        
        # Timeline visualization
        st.subheader("📅 Timeline Dự án")
        
        # Create Gantt chart data
        gantt_data = []
        for step_key, step_info in steps.items():
            step_data = current_project['master_plan'][step_key]
            if step_data['deadline']:
                gantt_data.append({
                    'Task': step_info['name'],
                    'Start': datetime.now().date().isoformat(),
                    'Finish': step_data['deadline'],
                    'Status': step_data['status'],
                    'Progress': step_data['progress']
                })
        
        if gantt_data:
            df_gantt = pd.DataFrame(gantt_data)
            fig = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Task", 
                            color="Status", title="Timeline Dự án")
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
