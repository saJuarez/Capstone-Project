--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

-- Started on 2024-10-27 23:53:26

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- TOC entry 4868 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 57346)
-- Name: jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.jobs (
    id integer NOT NULL,
    title character varying(255),
    description text,
    company character varying(255),
    location character varying(255),
    posted_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.jobs OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 57345)
-- Name: jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.jobs_id_seq OWNER TO postgres;

--
-- TOC entry 4869 (class 0 OID 0)
-- Dependencies: 219
-- Name: jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.id;


--
-- TOC entry 218 (class 1259 OID 40991)
-- Name: resume_feedback; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resume_feedback (
    id integer NOT NULL,
    user_id integer,
    resume_text text NOT NULL,
    feedback jsonb NOT NULL,
    upload_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.resume_feedback OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 40990)
-- Name: resume_feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.resume_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resume_feedback_id_seq OWNER TO postgres;

--
-- TOC entry 4870 (class 0 OID 0)
-- Dependencies: 217
-- Name: resume_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.resume_feedback_id_seq OWNED BY public.resume_feedback.id;


--
-- TOC entry 216 (class 1259 OID 40974)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(150) NOT NULL,
    email character varying(200) NOT NULL,
    password character varying(200) NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 40973)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 4871 (class 0 OID 0)
-- Dependencies: 215
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4701 (class 2604 OID 57349)
-- Name: jobs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs ALTER COLUMN id SET DEFAULT nextval('public.jobs_id_seq'::regclass);


--
-- TOC entry 4699 (class 2604 OID 40994)
-- Name: resume_feedback id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resume_feedback ALTER COLUMN id SET DEFAULT nextval('public.resume_feedback_id_seq'::regclass);


--
-- TOC entry 4698 (class 2604 OID 40977)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4862 (class 0 OID 57346)
-- Dependencies: 220
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.jobs (id, title, description, company, location, posted_date) FROM stdin;
\.


--
-- TOC entry 4860 (class 0 OID 40991)
-- Dependencies: 218
-- Data for Name: resume_feedback; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.resume_feedback (id, user_id, resume_text, feedback, upload_date) FROM stdin;
9	30	SAUL ADAM JUAREZ  \nAsheboro, NC | (336) 267-7273 | adam_juarez13@yahoo.com  \n  \nEDUCATION                                                                                             \nHigh School Diploma  \nBailey’s Grove Baptist School | Asheboro, NC                                                     August 2015 – May 2018  \n  \nBachelor of Science, Computer Science   \nUniversity of North Carolina in Greensboro | Greensboro                            August 2019 – December 2024 \nExperience with various languages such as C/C++, assembly, Python, JavaScript, HTML/CSS, and most prominently Java\nExperience with the development of programs from start to finish, including back-end and front-end functionality, as well as data management using MySQL\nWorked in teams on numerous occasions to complete programming projects by adapting an Agile methodology\n____________________________________________________________________________________ \nPROFESSIONAL EXPERIENCE  \nAutomotive Detailer                                                                                             June 2016 – January 2021  \nValvoline Express Care Car Wash | Asheboro, NC   \nWorked with fellow detailers in order to complete services requested by customers within a timely manner  \nFace-to-face experiences with customers including sales, appointment bookings, and conflict resolutions \nPerformed regular maintenance on the conveyorized car wash and its associated equipment\nTechnician II – Shipping and Receiving                                                           July 2018 – February 2023\nKI | High Point, NC  \nOperated and maintained specialized machinery and tools, such as plastic strapping machines and propane shrink guns to package furniture.\nNavigated BPCS in order to keep track of inventory to properly track all products and ensure each piece of furniture is loaded onto the proper freight trucks  \nCreated shipping labels, bills of lading, and package slips to provide clear and thorough documentation of the shipping of merchandise. \nSales Associate                                                                                                       June 2019 – August 2019  \nFurniture Market Warehouse | Asheboro and Greensboro, NC  \nHad extensive knowledge of products offered, such as a products material, manufacturer, sizes and measurements, prices, and sale prices to provide as much information to a customer and invoke a sale   \nGuided customers in choosing furniture that would best fit their home   \nCooperated with fellow sales associates to reach, maintain, and exceed sales goals\nSales Associate  \t              \t \t \t \t                   December 2020 – May 2021 \nAutoZone | Asheboro, NC \nDelivered parts to local automotive shops in a timely manner, ensuring they receive exactly what they need in order to do the job right\nProvided services to customers regarding their vehicles such as installing wiper blades, installing batteries, testing alternators, determining trouble codes, etc. \nMaintained the store floor, as well as the stocking area, to provide customers with easily accessible and conveniently placed products\nCAD Technician                                                                                                      February 2023 – Present\nKI | High Point, NC  \nProduce digital markers for each customer order by using Lectra Marker Manager and Diamino\nOccasionally digitize new patterns during their pre-production stage\nFrequently tasked with various problem-solving scenarios, whether it be cutting repairs or working with management to track down what went wrong during the production process of a product that does not reach our quality standards\n____________________________________________________________________________ \nCOMMUNITY ENGAGEMENT  \nTeam Infamous                                                                                       December 2018 – November 2019 \nCar Club | Central North Carolina  \nA car club consisting of 16 members around central North Carolina   \nHost various events for car enthusiasts to come together and enjoy car shows, contests, and more activities  \nCreate a welcoming atmosphere for car lovers to enjoy an uncommon hobby     \nSpartan Motor Club                                                                                    February 2019 – Present  \nCar Club | Greensboro, NC  \nOriginal member of the first automotive club at The University of North Carolina at Greensboro\nOrganized car meets and shows that are open to the public in order to socialize and develop relationships and connections with likeminded enthusiasts  \nEnsured members presence were frequently in attendance to local – and non-local – car events for self-promotion publicity  \n  	{"grades": {"Skills": {"score": 15, "feedback": "1. **Skills Section Evaluation:**\\n   - The skills section lacks clear organization and specificity. It would be beneficial to categorize the skills into technical skills (related to programming languages, software, tools), soft skills (teamwork, communication), and any certifications or specialized training.\\n   - The skills listed are somewhat relevant to the field of computer science, but they lack depth and specificity. For instance, mentioning proficiency levels (e.g., beginner, intermediate, advanced) in each programming language would provide a clearer picture of your capabilities.\\n   - It would be advantageous to include any relevant projects or achievements where these skills were applied, showcasing practical experience.\\n\\n2. **Ways to Enhance the Skills Section:**\\n   - **Technical Skills:** Clearly"}, "Education": {"score": 12, "feedback": "The candidate's educational background includes a Bachelor of Science in Computer Science from the University of North Carolina in Greensboro, which aligns well with the required qualifications for a job in the field. However, there are some areas for improvement in the education section:\\n\\n1. **High School Diploma**: While the completion of a high school diploma is relevant, it is not necessary to include it in the education section of the resume, especially when the candidate has a higher degree. Consider removing it to streamline the section.\\n\\n2. **Bachelor of Science, Computer Science**: The candidate's major in Computer Science is appropriate for most technical roles. However, the anticipated graduation date of December 2024 may raise concerns for potential employers as it indicates a significant gap between education"}, "Experience": {"score": 15, "feedback": "The experience described in the resume is not very relevant to a career in Computer Science. While the candidate does have a Bachelor's degree in Computer Science and experience with various programming languages, the majority of their work experience is in unrelated fields such as automotive detailing, shipping and receiving, sales, and car club involvement.\\n\\nTo improve the relevance of the resume for a Computer Science job, the candidate should focus on highlighting their technical skills, projects, internships, and relevant coursework related to programming, software development, and data management. They should provide specific examples of how they have applied their programming skills in real-world projects and demonstrate their ability to work in a team to complete programming tasks.\\n\\nAdditionally, the candidate could consider gaining more relevant experience through internships, freelance"}, "Formatting": {"score": 12, "feedback": "1. The resume lacks a clear and professional layout. It should include clear section headings such as \\"Summary,\\" \\"Education,\\" \\"Professional Experience,\\" \\"Skills,\\" etc., to make it easier for the reader to navigate.\\n\\n2. There is inconsistency in the formatting of dates in the \\"Education\\" section. Make sure to maintain a consistent format (e.g., Month Year – Month Year).\\n\\n3. The use of bullet points is inconsistent throughout the document. It is recommended to use bullet points consistently for each job description to enhance readability.\\n\\n4. The \\"Professional Experience\\" section should be presented in reverse-chronological order to highlight the most recent experience first.\\n\\n5. The descriptions under each job experience lack quantifiable achievements or specific examples of accomplishments."}, "Clarity and Grammar": {"score": 13, "feedback": "Overall, the resume is clear and well-organized. However, there are several areas that can be improved:\\n\\n1. **Objective Statement**: Consider adding a brief summary or objective statement at the beginning to highlight your key skills and career goals.\\n\\n2. **Education Section**: Provide more details about your Bachelor of Science in Computer Science, such as any relevant coursework, projects, or achievements. Also, mention any academic honors or awards.\\n\\n3. **Professional Experience**:\\n   - Provide more quantifiable achievements or results to demonstrate your impact in each role.\\n   - Use bullet points to make the information easier to read and highlight key responsibilities and accomplishments.\\n\\n4. **Language Skills**: Instead of just listing the programming languages you are familiar with, elaborate on projects"}}, "percentage": 89.33333333333333, "final_grade": "B", "total_score": 67}	2024-10-27 14:11:57.329297
10	31	M R. T\nEGAN URNER\n(850) 982-0124 | mc3megan@gmail.com | www.linkedin.com/in/megan-rose-turner\nEDUCATION\nMaster of Business Administration May 2025\nUNC Greensboro | Greensboro, NC\nBachelor of Science, Finance May 2022\nMinor: Music Performance\nUNC Greensboro | Greensboro, NC\nCompleted a variety of courses at UNC Greensboro like Economics, Businesses Computing, Accounting, Information\nSystems, Marketing and many more, along with my Finance curriculum\n__________________________________________________________________________________________________\nPROFESSIONAL EXPERIENCE\nSales Assistant Analyst January 2024 – Present\nPepsi Direct North America | Winston Salem, NC\n• Assist field representatives and Food Service representatives in maintaining a positive relationship with my\nassigned national portfolios, Sodexo and Ovation\n• Create and analyze sales reports each period for my assigned national portfolios to maintain and find ways to\npromote sales\n• Ensure all locations in my assigned national portfolios have updated and clean equipment that provide a diverse\narray of beverages that can satisfy a wide range of consumers\nFinance Coordinator June 2022 – November 2023\nPepsiCo Beverage North America | Winston Salem, NC\n• Created and analyze reports to track progression made on large customer accounts weekly\n• Managed multimillion dollar customer accounts by analyzing reports and problem solving through trends and\naging’s\n• Communicated with in house and outsourced bottling companies to facilitate payments and past due invoices\n• Worked within a team of 20 to 25 members to remedy all concerns and past due invoices for all customers to have\na smooth accounts receivable process\nJr Financial Analyst Intern June 2021 – April 2022\nPepsiCo Direct Food Service Coordinator | Winston Salem, NC\n• Ran rebate reports to ensure that each Pepsi customer receives the correct compensation\n• Organized receipts and expenditures to know the full scope of the budget\n• Gathered all information to make pricing forecasts that are applied to all customer contracts each year\nSeasonal Merchandise Associate November 2020 – January 2021 & June 2021 – August 2021\nHomeGoods | Cary, NC\n• Assisted HomeGoods shoppers with cash and card transactions through a cash register\n• Marketed the TJX Credit Card to all shoppers to save money and create loyal customers to HomeGoods\n• Provided a clean and organized stores to make all products accessible and to limit the Covid – 19 exposuresNorthwestern Mutual Internship July 2020 – November 2020\nCarolina Condrey Group | Greensboro, NC\n• Studied to become licensed in Life and Health insurance through the state of North Carolina\n• Worked with experienced Financial Advisors to get hands on experience with customers\n• Reached out to families and friends to help them with their financial goals and plans\nBrand Ambassador January 2020 – August 2020\nUNCG Career and Professional Development (CPD) | Greensboro, NC\n• Promoted different events CPD hosted on all their social media platforms\n• Represented and documented all the events that were hosted by CPD\n• Partnered with other Brand Ambassadors to create and publish the best, eye-catching content for the social media\nthat benefits UNCG students and alumni\nSpartan Guide Captain August 2019 – April 2022\nUNCG Undergraduate Admissions | Greensboro, NC\n• Introduced prospective students and parents to the UNCG campus\n• Memorized information about every department, program, and service on the UNCG’s campus\n• Created the tour schedule to ensure that all shifts are covered, and campus tours can function daily\n__________________________________________________________________________________________________\nSTUDENT ACTIVITIES AND ENGAGEMENT\nAssociate Vice President of Budget and Finance August 2021 – May 2022\nUNC Association of Student Governments | Chapel Hill, NC\n• Created, updated, and allocated the budget for UNC ASG\n• Hosted and organized working committees to better the UNC College System\n• Assisted the Vice President with any day-to-day activities that were needed\nBryan Student Ambassador May 2020 – August 2020\nBryan School of Business and Economics, UNCG | Greensboro, NC\n• Met with peers and professors to gather all the information to best represent the Bryan School of Business\n• Traveled around North Carolina to recruit and represent the Bryan School of Business\n• Helped facilitate and run Bryan School of Business events\nSecretary of Academic Affairs August 2019 – May 2020\nStudent Government Association, UNCG | Greensboro, NC\n• Represented students and their education to the university’s faculty\n• Sat on many different faculty committees to represent student voices\n• Met with the Provost to update the university’s faculty on student life and academic concerns from students\nFreshman Senator August 2018 – May 2019\nStudent Government Association, UNCG | Greensboro, NC\n• Served as a representative for the freshman class interest at UNCG\n• Shared concerns from first-year students with the larger senate and UNCG administration\n• Attended senate meetings, created legislation, and discussed current concerns\n__________________________________________________________________________________________________\nSKILLS\nOffice 2019: Microsoft Office Specialist: Excel Associate November 2021 – Present\n__________________________________________________________________________________________________COMMUNITY ENGAGEMENT\nTeam Infamous | Siler City, NC May 2019 – November 2019\n• Guided a car group with all their finances and investments by helping them save money for events and events,\ncollecting membership dues, and organizing money from events\nKidznotes | Durham, NC August 2017 – May 2018\n• Assisted music instructors with maintaining schedules, organizing materials, and teaching lessons\n__________________________________________________________________________________________________\nREFERENCES\nReferences available upon request	{"grades": {"Skills": {"score": 11, "feedback": "1. **Skills Section Evaluation:**\\n   - **Relevance:** The skills section is severely lacking in detail and breadth. The only skill mentioned is \\"Office 2019: Microsoft Office Specialist: Excel Associate.\\" This is too limited and does not adequately showcase the full range of skills you possess.\\n   - **Proficiency:** While being a Microsoft Office Specialist in Excel is a valuable skill, it is not sufficient on its own to highlight your capabilities effectively. Employers expect a broader set of skills, especially for roles in business, finance, and analysis.\\n\\n2. **Suggestions for Enhancing the Skills Section:**\\n   - **Include Core Business Skills:** Mention skills such as financial analysis, data analysis, market research, budgeting, financial modeling"}, "Education": {"score": 12, "feedback": "The educational background of the candidate does align with the required qualifications for the job, as they hold a Bachelor of Science degree in Finance and are currently pursuing a Master of Business Administration. However, the resume could benefit from more specific details about the courses taken during the MBA program that are relevant to the job they are applying for.\\n\\nIn terms of professional experience, the candidate has relevant experience in finance and sales analysis roles at PepsiCo, which is beneficial for positions that require financial acumen and analytical skills. The candidate should consider quantifying their achievements in these roles to demonstrate their impact and contributions more effectively.\\n\\nThe candidate's involvement in student activities and engagement showcases their leadership and organizational skills, which are valuable in a business environment. However, it might be helpful"}, "Portfolio": {"score": 14, "feedback": "The portfolio provided, which includes a resume and a list of experiences, is comprehensive in terms of the amount of information provided. However, there are several areas that could be improved:\\n\\n1. **Portfolio Organization**: The portfolio lacks a clear structure and formatting. It would benefit from a more professional layout with clearly defined sections for education, professional experience, student activities, skills, and community engagement.\\n\\n2. **Relevance of Information**: While the portfolio includes a wide range of experiences, not all of them may be relevant to the target industry or job roles. It's important to tailor the content to highlight skills and experiences that are most relevant to the positions being applied for.\\n\\n3. **Professional Experience Details**: The descriptions of professional experiences lack specificity and quant"}, "Experience": {"score": 11, "feedback": "Overall, the resume showcases a diverse range of experiences, but there are several areas that can be improved to make it more relevant for the targeted job. \\n\\n1. **Education Section**: The education section is well-detailed, but it lacks focus on specific courses or projects that are directly related to the finance or business field. Consider highlighting coursework or projects that demonstrate relevant skills and knowledge.\\n\\n2. **Professional Experience**:\\n   - **Sales Assistant Analyst**: While this role involves sales analysis and customer relations, it would be beneficial to emphasize more on financial analysis skills, budgeting, or any financial projects you worked on during your time at PepsiCo.\\n   - **Finance Coordinator**: This role is more aligned with finance, but the bullet points lack quant"}, "Formatting": {"score": 13, "feedback": "The organization and formatting of the resume could be improved for better presentation. Here are some suggestions:\\n\\n1. **Contact Information:** The contact information at the top should be more prominently displayed. Consider using a larger font size or bolding the text to make it stand out.\\n\\n2. **Section Headings:** Use clear and consistent section headings to make it easier for the reader to navigate the resume. Consider using a larger font size or bolding the headings to make them more noticeable.\\n\\n3. **Education Section:** The education section could be more streamlined. Instead of listing individual courses, focus on highlighting key achievements or projects during your academic experience.\\n\\n4. **Professional Experience:** Bullet points under each job role should be concise and focused on quantifiable achievements."}, "Clarity and Grammar": {"score": 13, "feedback": "The resume has several issues that need to be addressed:\\n\\n1. **Formatting**: The resume lacks a clear and professional format. The sections are not well-defined, and the overall layout appears cluttered. Consider using bullet points consistently and aligning the content properly.\\n\\n2. **Education Section**: The education section is minimal and lacks detail. Include relevant coursework, academic achievements, and any extracurricular involvement related to your field of study.\\n\\n3. **Professional Experience**: While the content is detailed, the bullet points are too lengthy. Try to be more concise and highlight key accomplishments and skills acquired in each role.\\n\\n4. **Skills Section**: The skills section is incomplete. Expand on your technical skills, software proficiency, and any certifications or relevant training"}}, "percentage": 82.22222222222221, "final_grade": "B", "total_score": 74}	2024-10-27 23:40:05.278709
\.


--
-- TOC entry 4858 (class 0 OID 40974)
-- Dependencies: 216
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password) FROM stdin;
26	test	test@gmail.com	pbkdf2:sha256:600000$KGSgqJrCWcRItRR2$e731d8a96e2aa75608707a71b8339a363ec7cf21022e9ed991db3a3beeff399f
27	joan	joan@gmail.com	pbkdf2:sha256:600000$rKZX15BpUElE5be0$de8213e0ba70fcb79f6f0e3c86867ad38c613ca76bb9dfa00f3383646d08f4b3
28	charles	charles@uncg.edu	pbkdf2:sha256:600000$Weoq9zO4FW1RrG3T$2c7a756df752f4c2e5177dd540ed848de3c349a5451c8d822ef734e343d3f217
29	meg	meg@gmail.com	pbkdf2:sha256:600000$GVeQRzkWTcA4xX2b$4852861554a1933d63bac2d080ead8d5c51633fe1dd3bb9e909836c562122c0e
30	greg	greg@gmail.com	pbkdf2:sha256:600000$z2uLzg7D6NoX4ONt$fac9416e9893aa968532394a5b419bd20e17abc6db41991fe6607ae4e1e58628
31	sarvesh	sarvesh@uncg.edu	pbkdf2:sha256:600000$nysBfttAncLBYS5A$cf359da2d98f2c6da3def4798cd0cff902723c11be1ee69f1cd1ce8fdd10bef4
\.


--
-- TOC entry 4872 (class 0 OID 0)
-- Dependencies: 219
-- Name: jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.jobs_id_seq', 1, false);


--
-- TOC entry 4873 (class 0 OID 0)
-- Dependencies: 217
-- Name: resume_feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.resume_feedback_id_seq', 10, true);


--
-- TOC entry 4874 (class 0 OID 0)
-- Dependencies: 215
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 31, true);


--
-- TOC entry 4712 (class 2606 OID 57354)
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- TOC entry 4710 (class 2606 OID 40999)
-- Name: resume_feedback resume_feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resume_feedback
    ADD CONSTRAINT resume_feedback_pkey PRIMARY KEY (id);


--
-- TOC entry 4704 (class 2606 OID 40987)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4706 (class 2606 OID 40979)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4708 (class 2606 OID 40985)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 4713 (class 2606 OID 41000)
-- Name: resume_feedback resume_feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resume_feedback
    ADD CONSTRAINT resume_feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


-- Completed on 2024-10-27 23:53:27

--
-- PostgreSQL database dump complete
--

