<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ระบบวิเคราะห์การสมัครงาน</title>
    <!-- Chosen Palette: Calm Neutral (BG: gray-50/white, Primary: blue-600, Text: slate-800) -->
    <!-- Application Structure Plan: ออกแบบเป็น Dashboard SPA 4 แท็บ (ภาพรวม, บริษัท, ผู้หางาน, ประกาศงาน) แทนการเลียนแบบโครงสร้างสไลด์ วัตถุประสงค์คือให้ผู้ใช้ (เช่น HR Manager หรือ Admin) สามารถสำรวจข้อมูลเชิงสัมพันธ์ได้ทันที เช่น คลิกบริษัทเพื่อดูงานที่โพสต์ หรือคลิกผู้หางานเพื่อดูประวัติการสมัคร โครงสร้างนี้เน้นการใช้งานและการสำรวจข้อมูล (Data Exploration) ที่ง่ายและตรงไปตรงมาที่สุด -->
    <!-- Visualization & Content Choices: [ภาพรวม: 4 KPIs (HTML Card) / การสมัครงานตามเวลา (Line Chart - Chart.js) / สถานะการสมัคร (Donut Chart - Chart.js)] [บริษัท/ผู้หางาน/ประกาศงาน: ใช้โครงสร้าง 3 แท็บแยกกัน แต่ละแท็บมี List + Detail View (HTML/JS) และช่องค้นหา (JS Filter)] [การเชื่อมโยงข้อมูล (ERD): แสดงผลผ่านการคลิก (Click Interaction) เช่น คลิกบริษัท -> แสดงงานของบริษัท (JS Logic) ซึ่งเป็นการนำเสนอความสัมพันธ์แบบ 1-to-Many โดยไม่ใช้ไดอะแกรม] [ยืนยัน: ไม่ใช้ SVG/Mermaid ใช้ Canvas สำหรับชาร์ต และ HTML/Tailwind สำหรับโครงสร้างทั้งหมด] -->
    <!-- CONFIRMATION: NO SVG graphics used. NO Mermaid JS used. -->
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sarabun:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        body {
            font-family: 'Sarabun', 'Inter', sans-serif;
            background-color: #f8fafc; /* bg-gray-50 */
        }
        
        /* สไตล์สำหรับ Chart Container ตามข้อกำหนด */
        .chart-container {
            position: relative;
            width: 100%;
            max-width: 48rem; /* max-w-2xl */
            margin-left: auto;
            margin-right: auto;
            height: 24rem; /* h-96 */
            max-height: 24rem; /* max-h-96 */
        }

        /* สไตล์สำหรับ Mobile Chart */
        @media (max-width: 768px) {
            .chart-container {
                height: 20rem; /* h-80 */
                max-height: 20rem; /* max-h-80 */
            }
        }
        
        /* สไตล์สำหรับ Active Tab */
        .tab-btn.active {
            border-color: #2563eb; /* border-blue-600 */
            background-color: #dbeafe; /* bg-blue-100 */
            color: #1e3a8a; /* text-blue-800 */
            font-weight: 600;
        }
        
        /* ซ่อน/แสดง Tab Content */
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        
        /* สไตล์สำหรับ Scrollable List */
        .data-list {
            max-height: 70vh;
            overflow-y: auto;
        }
    </style>
</head>
<body class="text-slate-800">

    <div class="max-w-7xl mx-auto p-4 md:p-8">
        
        <header class="mb-6">
            <h1 class="text-3xl md:text-4xl font-bold text-blue-800">ระบบวิเคราะห์การสมัครงาน</h1>
            <p class="text-lg text-slate-600">แดชบอร์ดสรุปข้อมูลจากระบบจัดการการสมัครงาน</p>
        </header>

        <!-- Navigation Tabs -->
        <nav class="flex flex-wrap gap-2 mb-6">
            <button class="tab-btn active text-sm md:text-base px-4 py-2 rounded-lg border-b-4 border-transparent hover:bg-blue-50 transition-all" data-tab="overview">
                ภาพรวมระบบ
            </button>
            <button class="tab-btn text-sm md:text-base px-4 py-2 rounded-lg border-b-4 border-transparent hover:bg-blue-50 transition-all" data-tab="companies">
                ข้อมูลบริษัท
            </button>
            <button class="tab-btn text-sm md:text-base px-4 py-2 rounded-lg border-b-4 border-transparent hover:bg-blue-50 transition-all" data-tab="seekers">
                ข้อมูลผู้หางาน
            </button>
            <button class="tab-btn text-sm md:text-base px-4 py-2 rounded-lg border-b-4 border-transparent hover:bg-blue-50 transition-all" data-tab="jobs">
                ข้อมูลประกาศงาน
            </button>
        </nav>

        <!-- Tab Content Area -->
        <main>
            <!-- =======================
                 Tab 1: ภาพรวม (Overview)
                 ======================= -->
            <section id="overview" class="tab-content active space-y-8">
                <p class="text-base text-slate-700 bg-white p-4 rounded-lg shadow-sm">
                    หน้านี้แสดงภาพรวมสถิติที่สำคัญที่สุดของระบบ (Key Metrics) รวมถึงแนวโน้มการสมัครงานในช่วงเวลาต่างๆ และสัดส่วนสถานะของใบสมัครทั้งหมด (เช่น รอดำเนินการ, เรียกสัมภาษณ์) เพื่อให้เห็นภาพรวมของประสิทธิภาพระบบ
                </p>
                
                <!-- Key Metrics -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="bg-white p-6 rounded-lg shadow-sm border-l-4 border-blue-500">
                        <h3 class="text-sm font-medium text-slate-500 uppercase">บริษัททั้งหมด</h3>
                        <p id="metric-companies" class="text-4xl font-bold text-blue-800">0</p>
                    </div>
                    <div class="bg-white p-6 rounded-lg shadow-sm border-l-4 border-green-500">
                        <h3 class="text-sm font-medium text-slate-500 uppercase">ผู้หางานทั้งหมด</h3>
                        <p id="metric-seekers" class="text-4xl font-bold text-green-800">0</p>
                    </div>
                    <div class="bg-white p-6 rounded-lg shadow-sm border-l-4 border-indigo-500">
                        <h3 class="text-sm font-medium text-slate-500 uppercase">ประกาศงาน (Active)</h3>
                        <p id="metric-jobs" class="text-4xl font-bold text-indigo-800">0</p>
                    </div>
                    <div class="bg-white p-6 rounded-lg shadow-sm border-l-4 border-amber-500">
                        <h3 class="text-sm font-medium text-slate-500 uppercase">การสมัครทั้งหมด</h3>
                        <p id="metric-applications" class="text-4xl font-bold text-amber-800">0</p>
                    </div>
                </div>
                
                <!-- Charts -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div class="bg-white p-6 rounded-lg shadow-sm">
                        <h3 class="text-xl font-semibold mb-4">แนวโน้มการสมัครงาน (30 วันย้อนหลัง)</h3>
                        <div class="chart-container">
                            <canvas id="applicationsChart"></canvas>
                        </div>
                    </div>
                    <div class="bg-white p-6 rounded-lg shadow-sm">
                        <h3 class="text-xl font-semibold mb-4">สัดส่วนสถานะใบสมัคร</h3>
                        <div class="chart-container">
                            <canvas id="statusChart"></canvas>
                        </div>
                    </div>
                </div>
            </section>

            <!-- =======================
                 Tab 2: บริษัท (Companies)
                 ======================= -->
            <section id="companies" class="tab-content space-y-6">
                <p class="text-base text-slate-700 bg-white p-4 rounded-lg shadow-sm">
                    สำรวจข้อมูลบริษัทที่ลงทะเบียนในระบบ ค้นหาบริษัท และคลิกที่ชื่อบริษัทเพื่อดูรายละเอียดโปรไฟล์ และรายชื่องานทั้งหมดที่บริษัทนั้นๆ กำลังประกาศรับสมัคร (แสดงความสัมพันธ์ 1-to-Many ระหว่าง Company และ JobPost)
                </p>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- List Column -->
                    <div class="md:col-span-1 bg-white p-4 rounded-lg shadow-sm">
                        <input type="text" id="companySearch" class="w-full px-3 py-2 border rounded-lg mb-4" placeholder="ค้นหาชื่อบริษัท...">
                        <ul id="companyList" class="data-list divide-y divide-gray-200">
                            <!-- JS will populate this -->
                        </ul>
                    </div>
                    <!-- Detail Column -->
                    <div class="md:col-span-2 bg-white p-6 rounded-lg shadow-sm min-h-[300px]">
                        <div id="companyDetail">
                            <p class="text-slate-500 text-center mt-12">กรุณาเลือกบริษัทจากรายการด้านซ้าย</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- =========================
                 Tab 3: ผู้หางาน (Job Seekers)
                 ========================= -->
            <section id="seekers" class="tab-content space-y-6">
                <p class="text-base text-slate-700 bg-white p-4 rounded-lg shadow-sm">
                    สำรวจข้อมูลผู้หางานในระบบ ค้นหาผู้หางาน และคลิกที่ชื่อเพื่อดูโปรไฟล์, ทักษะ (Skills), และประวัติการศึกษา (Education) รวมถึงประวัติการสมัครงานทั้งหมด (แสดงความสัมพันธ์ Many-to-Many ผ่านตาราง Application)
                </p>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- List Column -->
                    <div class="md:col-span-1 bg-white p-4 rounded-lg shadow-sm">
                        <input type="text" id="seekerSearch" class="w-full px-3 py-2 border rounded-lg mb-4" placeholder="ค้นหาชื่อผู้หางาน...">
                        <ul id="seekerList" class="data-list divide-y divide-gray-200">
                            <!-- JS will populate this -->
                        </ul>
                    </div>
                    <!-- Detail Column -->
                    <div class="md:col-span-2 bg-white p-6 rounded-lg shadow-sm min-h-[300px]">
                        <div id="seekerDetail">
                            <p class="text-slate-500 text-center mt-12">กรุณาเลือกผู้หางานจากรายการด้านซ้าย</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- ========================
                 Tab 4: ประกาศงาน (Job Posts)
                 ======================== -->
            <section id="jobs" class="tab-content space-y-6">
                <p class="text-base text-slate-700 bg-white p-4 rounded-lg shadow-sm">
                    สำรวจประกาศงานทั้งหมดในระบบ ค้นหาตำแหน่งงาน และคลิกที่ชื่องานเพื่อดูรายละเอียด, คุณสมบัติ (Requirements) และที่สำคัญคือ "รายชื่อผู้สมัคร" สำหรับตำแหน่งนั้นๆ (แสดงความสามารถในการคัดกรองตามสไลด์ [115])
                </p>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- List Column -->
                    <div class="md:col-span-1 bg-white p-4 rounded-lg shadow-sm">
                        <input type="text" id="jobSearch" class="w-full px-3 py-2 border rounded-lg mb-4" placeholder="ค้นหาตำแหน่งงาน...">
                        <ul id="jobList" class="data-list divide-y divide-gray-200">
                            <!-- JS will populate this -->
                        </ul>
                    </div>
                    <!-- Detail Column -->
                    <div class="md:col-span-2 bg-white p-6 rounded-lg shadow-sm min-h-[300px]">
                        <div id="jobDetail">
                            <p class="text-slate-500 text-center mt-12">กรุณาเลือกประกาศงานจากรายการด้านซ้าย</p>
                        </div>
                    </div>
                </div>
            </section>
        </main>

    </div>

    <script>
        // Utility function to safely escape HTML to prevent XSS
        function escapeHTML(str) {
            return str.replace(/[&<>"']/g, function(m) {
                return {
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#39;'
                }[m];
            });
        }
        
        // --- 1. MOCK DATA (based on Data Dictionary) ---
        // ข้อมูลจำลองตามโครงสร้าง ER-Diagram [108] และ Data Dictionary [146-159]
        const companies = [
            { id: 1, name: 'TechNova Solutions Ltd.', email: 'hr@technova.com', address: '101 Cyber Tower, Ratchada, Bangkok', contact: '02-111-2222' },
            { id: 2, name: 'CreativeFlow Agency', email: 'join@creativeflow.agency', address: '55 T-One Building, Sukhumvit 40', contact: '02-333-4444' },
            { id: 3, name: 'CapitalBank (Thailand)', email: 'careers@capitalbank.th', address: '33 Sathorn Rd, Bangkok', contact: '02-555-6666' },
            { id: 4, name: 'GreenSprout Start-up', email: 'hello@greensprout.io', address: 'Remote (Thailand)', contact: '081-777-8888' }
        ];

        const jobSeekers = [
            { id: 101, name: 'วริศรา สระศรีสม', email: 'warisara@email.com', education: 'B.Eng. Computer Engineering', skills: 'React, TypeScript, Node.js, Next.js', experience: '2 years as Frontend Developer' },
            { id: 102, name: 'จิดาภา เติมสินสุข', email: 'jidapa@email.com', education: 'B.A. Communication Design', skills: 'Figma, Sketch, Adobe XD, User Research', experience: '3 years as UX/UI Designer' },
            { id: 103, name: 'ธีรดา พุ่มเจริญ', email: 'theerada@email.com', education: 'M.Sc. Data Science', skills: 'SQL, Python (Pandas, Scikit-learn), Tableau', experience: '4 years as Data Analyst' },
            { id: 104, name: 'สมชาย ใจดี', email: 'somchai@email.com', education: 'B.B.A. Marketing', skills: 'SEO, Google Ads, Content Strategy', experience: '5 years as Digital Marketing Specialist' },
            { id: 105, name: 'อาทิตย์ โปรแกรมเมอร์', email: 'arthit@email.com', education: 'B.Eng. Computer Engineering', skills: 'Java, Spring Boot, Microservices, Kafka', experience: '8 years as Senior Backend Developer' }
        ];

        const jobPosts = [
            { id: 1001, companyId: 1, position: 'Frontend Developer (React)', description: 'Build beautiful and responsive user interfaces for our web applications.', requirements: '2+ years React, TypeScript, HTML/CSS. Strong understanding of REST APIs.', postDate: '2025-11-01', closingDate: '2025-12-01' },
            { id: 1002, companyId: 2, position: 'UX/UI Designer', description: 'Design user-centric experiences for our clients projects.', requirements: '3+ years in Figma, Sketch. A strong portfolio is required.', postDate: '2025-11-02', closingDate: '2025-12-02' },
            { id: 1003, companyId: 1, position: 'Senior Backend Developer (Java)', description: 'Develop and maintain our core banking microservices.', requirements: '5+ years Java, Spring Boot, SQL. Experience with Kafka is a plus.', postDate: '2025-10-25', closingDate: '2025-11-25' },
            { id: 1004, companyId: 3, position: 'Financial Analyst', description: 'Analyze financial data and create reports for management.', requirements: 'Bachelors in Finance or Accounting. 2+ years experience.', postDate: '2025-11-05', closingDate: '2025-11-30' },
            { id: 1005, companyId: 2, position: 'Digital Marketing Specialist', description: 'Manage SEO/SEM and social media campaigns.', requirements: '4+ years in digital marketing, proven experience with Google Analytics.', postDate: '2025-10-30', closingDate: '2025-11-30' }
        ];

        const applications = [
            { id: 5001, jobId: 1001, seekerId: 101, applyDate: '2025-11-02', status: 'interview' },
            { id: 5002, jobId: 1002, seekerId: 102, applyDate: '2025-11-03', status: 'pending' },
            { id: 5003, jobId: 1003, seekerId: 105, applyDate: '2025-10-26', status: 'interview' },
            { id: 5004, jobId: 1004, seekerId: 103, applyDate: '2025-11-06', status: 'reviewing' },
            { id: 5005, jobId: 1005, seekerId: 104, applyDate: '2025-11-01', status: 'pending' },
            { id: 5006, jobId: 1001, seekerId: 103, applyDate: '2025-11-04', status: 'rejected' },
            { id: 5007, jobId: 1003, seekerId: 101, applyDate: '2025-10-28', status: 'rejected' },
            { id: 5008, jobId: 1002, seekerId: 101, applyDate: '2025-11-05', status: 'pending' }
        ];

        // --- 2. Chart Utility Functions ---
        
        // ฟังก์ชันสำหรับ Tooltip ของ Chart.js (ตามข้อกำหนด)
        const getOrCreateTooltip = (chart) => {
            let tooltipEl = chart.canvas.parentNode.querySelector('div');
            if (!tooltipEl) {
                tooltipEl = document.createElement('div');
                tooltipEl.style.background = 'rgba(0, 0, 0, 0.7)';
                tooltipEl.style.borderRadius = '3px';
                tooltipEl.style.color = 'white';
                tooltipEl.style.opacity = 1;
                tooltipEl.style.pointerEvents = 'none';
                tooltipEl.style.position = 'absolute';
                tooltipEl.style.transform = 'translate(-50%, 0)';
                tooltipEl.style.transition = 'all .1s ease';
                tooltipEl.style.padding = '6px';
                tooltipEl.style.fontSize = '12px';
                
                const table = document.createElement('table');
                table.style.margin = '0px';

                tooltipEl.appendChild(table);
                chart.canvas.parentNode.appendChild(tooltipEl);
            }
            return tooltipEl;
        };

        const externalTooltipHandler = (context) => {
            const {chart, tooltip} = context;
            const tooltipEl = getOrCreateTooltip(chart);

            if (tooltip.opacity === 0) {
                tooltipEl.style.opacity = 0;
                return;
            }

            if (tooltip.body) {
                const titleLines = tooltip.title || [];
                const bodyLines = tooltip.body.map(b => b.lines);

                const tableHead = document.createElement('thead');
                titleLines.forEach(title => {
                    const tr = document.createElement('tr');
                    tr.style.borderWidth = 0;
                    const th = document.createElement('th');
                    th.style.borderWidth = 0;
                    th.style.textAlign = 'left';
                    const text = document.createTextNode(title);
                    th.appendChild(text);
                    tr.appendChild(th);
                    tableHead.appendChild(tr);
                });

                const tableBody = document.createElement('tbody');
                bodyLines.forEach((body, i) => {
                    const colors = tooltip.labelColors[i];
                    const span = document.createElement('span');
                    span.style.background = colors.backgroundColor;
                    span.style.borderColor = colors.borderColor;
                    span.style.borderWidth = '2px';
                    span.style.marginRight = '10px';
                    span.style.height = '10px';
                    span.style.width = '10px';
                    span.style.display = 'inline-block';

                    const tr = document.createElement('tr');
                    tr.style.backgroundColor = 'inherit';
                    tr.style.borderWidth = 0;

                    const td = document.createElement('td');
                    td.style.borderWidth = 0;

                    const text = document.createTextNode(body);

                    td.appendChild(span);
                    td.appendChild(text);
                    tr.appendChild(td);
                    tableBody.appendChild(tr);
                });

                const tableRoot = tooltipEl.querySelector('table');
                while (tableRoot.firstChild) {
                    tableRoot.firstChild.remove();
                }
                tableRoot.appendChild(tableHead);
                tableRoot.appendChild(tableBody);
            }

            const {offsetLeft: positionX, offsetTop: positionY} = chart.canvas;
            tooltipEl.style.opacity = 1;
            tooltipEl.style.left = positionX + tooltip.caretX + 'px';
            tooltipEl.style.top = positionY + tooltip.caretY + 'px';
            tooltipEl.style.transform = 'translate(-50%, -100%)';
            tooltipEl.style.padding = tooltip.options.padding + 'px ' + tooltip.options.padding + 'px';
        };

        // ฟังก์ชันสำหรับตัดข้อความในแกน X (ตามข้อกำหนด 16-char)
        function formatLabel(value, maxChars = 16) {
            const str = String(value);
            if (str.length > maxChars) {
                return str.substring(0, maxChars) + '...';
            }
            return str;
        }

        
        document.addEventListener('DOMContentLoaded', () => {
            
            // --- 3. Tab Navigation Logic ---
            const tabButtons = document.querySelectorAll('.tab-btn');
            const tabContents = document.querySelectorAll('.tab-content');

            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const tabName = button.dataset.tab;
                    
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    button.classList.add('active');
                    
                    tabContents.forEach(content => {
                        content.classList.remove('active');
                        if (content.id === tabName) {
                            content.classList.add('active');
                        }
                    });
                });
            });

            // --- 4. Render Tab 1: Overview ---
            function renderOverviewTab() {
                // 4.1. Key Metrics
                document.getElementById('metric-companies').textContent = companies.length;
                document.getElementById('metric-seekers').textContent = jobSeekers.length;
                document.getElementById('metric-jobs').textContent = jobPosts.length;
                document.getElementById('metric-applications').textContent = applications.length;

                // 4.2. Applications Line Chart
                const appDates = applications.map(app => app.applyDate.split('T')[0]);
                const appCounts = appDates.reduce((acc, date) => {
                    acc[date] = (acc[date] || 0) + 1;
                    return acc;
                }, {});
                const sortedDates = Object.keys(appCounts).sort();
                const lineCtx = document.getElementById('applicationsChart').getContext('2d');
                new Chart(lineCtx, {
                    type: 'line',
                    data: {
                        labels: sortedDates,
                        datasets: [{
                            label: 'จำนวนการสมัคร',
                            data: sortedDates.map(date => appCounts[date]),
                            borderColor: '#2563eb', // blue-600
                            backgroundColor: 'rgba(37, 99, 235, 0.1)',
                            fill: true,
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false, // ตามข้อกำหนด
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                enabled: false,
                                position: 'nearest',
                                external: externalTooltipHandler
                            }
                        },
                        scales: {
                            x: {
                                ticks: {
                                    callback: (val, index) => formatLabel(sortedDates[index])
                                }
                            }
                        }
                    }
                });
                
                // 4.3. Status Donut Chart
                const statusCounts = applications.reduce((acc, app) => {
                    acc[app.status] = (acc[app.status] || 0) + 1;
                    return acc;
                }, {});
                const statusLabels = Object.keys(statusCounts);
                const statusData = Object.values(statusCounts);
                const donutCtx = document.getElementById('statusChart').getContext('2d');
                new Chart(donutCtx, {
                    type: 'doughnut',
                    data: {
                        labels: statusLabels.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
                        datasets: [{
                            label: 'สถานะใบสมัคร',
                            data: statusData,
                            backgroundColor: ['#f59e0b', '#3b82f6', '#10b981', '#ef4444', '#8b5cf6'], // amber, blue, green, red, violet
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false, // ตามข้อกำหนด
                        plugins: {
                            legend: { position: 'bottom' },
                            tooltip: {
                                enabled: false,
                                position: 'nearest',
                                external: externalTooltipHandler
                            }
                        }
                    }
                });
            }

            // --- 5. Render Tab 2: Companies ---
            function renderCompanyTab() {
                const listEl = document.getElementById('companyList');
                const detailEl = document.getElementById('companyDetail');
                const searchEl = document.getElementById('companySearch');
                
                function showCompanyDetail(companyId) {
                    const company = companies.find(c => c.id === companyId);
                    const jobs = jobPosts.filter(j => j.companyId === companyId);
                    
                    let jobsHtml = jobs.length > 0
                        ? jobs.map(job => `<li class="py-2 px-3 rounded-md bg-indigo-50">${escapeHTML(job.position)}</li>`).join('')
                        : '<p class="text-slate-500">ยังไม่มีประกาศงาน</p>';

                    detailEl.innerHTML = `
                        <h2 class="text-2xl font-bold mb-2">${escapeHTML(company.name)}</h2>
                        <p class="text-slate-600 mb-1"><strong>อีเมล:</strong> ${escapeHTML(company.email)}</p>
                        <p class="text-slate-600 mb-1"><strong>ติดต่อ:</strong> ${escapeHTML(company.contact)}</p>
                        <p class="text-slate-600 mb-4"><strong>ที่อยู่:</strong> ${escapeHTML(company.address)}</p>
                        <hr class="my-4">
                        <h3 class="text-xl font-semibold mb-3">ประกาศงานของบริษัทนี้:</h3>
                        <ul class="space-y-2">${jobsHtml}</ul>
                    `;
                }
                
                function populateList(filter = '') {
                    listEl.innerHTML = '';
                    const filteredCompanies = companies.filter(c => c.name.toLowerCase().includes(filter.toLowerCase()));
                    
                    if (filteredCompanies.length === 0) {
                        listEl.innerHTML = '<li class="p-4 text-slate-500">ไม่พบข้อมูลบริษัท</li>';
                        return;
                    }
                    
                    filteredCompanies.forEach(company => {
                        const li = document.createElement('li');
                        li.className = 'p-4 hover:bg-blue-100 cursor-pointer rounded-lg transition-colors';
                        li.textContent = company.name;
                        li.dataset.id = company.id;
                        li.addEventListener('click', () => {
                            showCompanyDetail(company.id);
                            // Highlight active item
                            listEl.querySelectorAll('li').forEach(item => item.classList.remove('bg-blue-200', 'font-semibold'));
                            li.classList.add('bg-blue-200', 'font-semibold');
                        });
                        listEl.appendChild(li);
                    });
                }
                
                searchEl.addEventListener('input', (e) => populateList(e.target.value));
                populateList(); // Initial load
            }

            // --- 6. Render Tab 3: Job Seekers ---
            function renderSeekerTab() {
                const listEl = document.getElementById('seekerList');
                const detailEl = document.getElementById('seekerDetail');
                const searchEl = document.getElementById('seekerSearch');

                function showSeekerDetail(seekerId) {
                    const seeker = jobSeekers.find(s => s.id === seekerId);
                    const seekerApps = applications.filter(app => app.seekerId === seekerId);
                    
                    let appsHtml = seekerApps.length > 0
                        ? seekerApps.map(app => {
                            const job = jobPosts.find(j => j.id === app.jobId);
                            const company = companies.find(c => c.id === job.companyId);
                            return `
                                <li class="py-2 px-3 rounded-md bg-green-50">
                                    <span class="font-semibold">${escapeHTML(job.position)}</span> at ${escapeHTML(company.name)}
                                    <span class="ml-2 px-2 py-0.5 rounded-full text-xs ${app.status === 'interview' ? 'bg-blue-200 text-blue-800' : app.status === 'rejected' ? 'bg-red-200 text-red-800' : 'bg-gray-200 text-gray-800'}">
                                        ${escapeHTML(app.status)}
                                    </span>
                                </li>`;
                        }).join('')
                        : '<p class="text-slate-500">ยังไม่มีประวัติการสมัครงาน</p>';

                    detailEl.innerHTML = `
                        <h2 class="text-2xl font-bold mb-2">${escapeHTML(seeker.name)}</h2>
                        <p class="text-slate-600 mb-1"><strong>อีเมล:</strong> ${escapeHTML(seeker.email)}</p>
                        <p class="text-slate-600 mb-1"><strong>การศึกษา:</strong> ${escapeHTML(seeker.education)}</p>
                        <p class="text-slate-600 mb-1"><strong>ประสบการณ์:</strong> ${escapeHTML(seeker.experience)}</p>
                        <p class="text-slate-600 mb-4"><strong>ทักษะ:</strong> ${escapeHTML(seeker.skills)}</p>
                        <hr class="my-4">
                        <h3 class="text-xl font-semibold mb-3">ประวัติการสมัครงาน:</h3>
                        <ul class="space-y-2">${appsHtml}</ul>
                    `;
                }

                function populateList(filter = '') {
                    listEl.innerHTML = '';
                    const filteredSeekers = jobSeekers.filter(s => s.name.toLowerCase().includes(filter.toLowerCase()));
                    
                    if (filteredSeekers.length === 0) {
                        listEl.innerHTML = '<li class="p-4 text-slate-500">ไม่พบข้อมูลผู้หางาน</li>';
                        return;
                    }

                    filteredSeekers.forEach(seeker => {
                        const li = document.createElement('li');
                        li.className = 'p-4 hover:bg-blue-100 cursor-pointer rounded-lg transition-colors';
                        li.textContent = seeker.name;
                        li.dataset.id = seeker.id;
                        li.addEventListener('click', () => {
                            showSeekerDetail(seeker.id);
                            listEl.querySelectorAll('li').forEach(item => item.classList.remove('bg-blue-200', 'font-semibold'));
                            li.classList.add('bg-blue-200', 'font-semibold');
                        });
                        listEl.appendChild(li);
                    });
                }
                
                searchEl.addEventListener('input', (e) => populateList(e.target.value));
                populateList(); // Initial load
            }
            
            // --- 7. Render Tab 4: Job Posts ---
            function renderJobTab() {
                const listEl = document.getElementById('jobList');
                const detailEl = document.getElementById('jobDetail');
                const searchEl = document.getElementById('jobSearch');

                function showJobDetail(jobId) {
                    const job = jobPosts.find(j => j.id === jobId);
                    const company = companies.find(c => c.id === job.companyId);
                    const jobApps = applications.filter(app => app.jobId === jobId);

                    let appsHtml = jobApps.length > 0
                        ? jobApps.map(app => {
                            const seeker = jobSeekers.find(s => s.id === app.seekerId);
                            return `
                                <li class="py-2 px-3 rounded-md bg-amber-50 flex justify-between items-center">
                                    <div>
                                        <span class="font-semibold">${escapeHTML(seeker.name)}</span>
                                        <span class="text-sm text-slate-600 ml-2">(${escapeHTML(seeker.skills)})</span>
                                    </div>
                                    <span class="px-2 py-0.5 rounded-full text-xs ${app.status === 'interview' ? 'bg-blue-200 text-blue-800' : app.status === 'rejected' ? 'bg-red-200 text-red-800' : 'bg-gray-200 text-gray-800'}">
                                        ${escapeHTML(app.status)}
                                    </span>
                                </li>`;
                        }).join('')
                        : '<p class="text-slate-500">ยังไม่มีผู้สมัครสำหรับงานนี้</p>';

                    detailEl.innerHTML = `
                        <h2 class="text-2xl font-bold mb-1">${escapeHTML(job.position)}</h2>
                        <p class="text-lg text-slate-600 mb-2 font-medium">${escapeHTML(company.name)}</p>
                        <p class="text-sm text-slate-500 mb-4">ประกาศเมื่อ: ${job.postDate} | ปิดรับ: ${job.closingDate}</p>
                        <p class="text-slate-700 mb-2"><strong>รายละเอียดงาน:</strong> ${escapeHTML(job.description)}</p>
                        <p class="text-slate-700 mb-4"><strong>คุณสมบัติ:</strong> ${escapeHTML(job.requirements)}</p>
                        <hr class="my-4">
                        <h3 class="text-xl font-semibold mb-3">รายชื่อผู้สมัคร (${jobApps.length} คน):</h3>
                        <ul class="space-y-2">${appsHtml}</ul>
                    `;
                }

                function populateList(filter = '') {
                    listEl.innerHTML = '';
                    const filteredJobs = jobPosts.filter(j => j.position.toLowerCase().includes(filter.toLowerCase()));
                    
                    if (filteredJobs.length === 0) {
                        listEl.innerHTML = '<li class="p-4 text-slate-500">ไม่พบข้อมูลประกาศงาน</li>';
                        return;
                    }

                    filteredJobs.forEach(job => {
                        const li = document.createElement('li');
                        li.className = 'p-4 hover:bg-blue-100 cursor-pointer rounded-lg transition-colors';
                        li.innerHTML = `
                            <span class="font-medium">${escapeHTML(job.position)}</span>
                            <span class="block text-sm text-slate-600">${escapeHTML(companies.find(c => c.id === job.companyId).name)}</span>
                        `;
                        li.dataset.id = job.id;
                        li.addEventListener('click', () => {
                            showJobDetail(job.id);
                            listEl.querySelectorAll('li').forEach(item => item.classList.remove('bg-blue-200'));
                            li.classList.add('bg-blue-200');
                        });
                        listEl.appendChild(li);
                    });
                }
                
                searchEl.addEventListener('input', (e) => populateList(e.target.value));
                populateList(); // Initial load
            }

            // --- 8. Initial Render ---
            renderOverviewTab();
            renderCompanyTab();
            renderSeekerTab();
            renderJobTab();
        });
    </script>
</body>
</html>
