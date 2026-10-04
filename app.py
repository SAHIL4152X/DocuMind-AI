import streamlit as st
from src.loader import load_pdf
from src.splitter import split_documents
from src.embeddings import create_embedding
from src.vectorstore import get_vector_store, create_vector_store
from src.retriever import search_documents
from src.prompts import create_qa_prompt
from src.llm import generate_answer
from src.mcq import generate_mcqs, check_answers
from src.important_questions import generate_important_questions
from src.summary import generate_summary

from pathlib import Path


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# TOOL OPTIONS
# =========================================================

tools = [
    "💬 Ask AI",
    "📝 Generate MCQs",
    "🎯 Important Questions",
    "📖 PDF Summary"
]


# =========================================================
# SESSION STATE
# =========================================================

if "sidebar_tool" not in st.session_state:
    st.session_state["sidebar_tool"] = "💬 Ask AI"

if "processed" not in st.session_state:
    st.session_state["processed"] = False

if "ask_ai_history" not in st.session_state:
    st.session_state["ask_ai_history"] = []

if "mcq_submitted" not in st.session_state:
    st.session_state["mcq_submitted"] = False

if "processed_documents" not in st.session_state:
    st.session_state["processed_documents"] = {}

if "mcqs_by_document" not in st.session_state:
    st.session_state["mcqs_by_document"] = {}

if "mcq_submitted_by_document" not in st.session_state:
    st.session_state["mcq_submitted_by_document"] = {}

if "mcq_score_by_document" not in st.session_state:
    st.session_state["mcq_score_by_document"] = {}

if "mcq_results_by_document" not in st.session_state:
    st.session_state["mcq_results_by_document"] = {}

if "important_questions_by_document" not in st.session_state:
    st.session_state["important_questions_by_document"] = {}

if "pdf_summaries_by_document" not in st.session_state:
    st.session_state["pdf_summaries_by_document"] = {}   


# =========================================================
# TOOL SELECTOR CALLBACK
# =========================================================

def select_tool(tool_name):
    st.session_state["sidebar_tool"] = tool_name


# =========================================================
# SIDEBAR
# =========================================================

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("📚 DocuMind AI")

    st.caption("Your PDF study companion")

    st.divider()

    st.subheader("Study Tools")

    tool = st.radio(
        "Choose a tool",
        tools,
        key="sidebar_tool",
        label_visibility="collapsed"
    )

    st.divider()

    st.subheader("Appearance")

    dark_mode = st.toggle(
        "Dark mode",
        value=True
    )

    st.divider()

    # =========================================================
# CLEAR STUDY RESULTS
# =========================================================

with st.sidebar:

    st.divider()

    st.subheader("🧹 Clear Study Results")

    if st.button(
        "Clear Study Results",
        use_container_width=True
    ):

        # Clear Ask AI history
        st.session_state["ask_ai_history"] = []

        # Clear PDF-wise MCQ data
        st.session_state["mcqs_by_document"] = {}
        st.session_state["mcq_submitted_by_document"] = {}
        st.session_state["mcq_score_by_document"] = {}
        st.session_state["mcq_results_by_document"] = {}

        # Clear PDF-wise Important Questions
        st.session_state["important_questions_by_document"] = {}

        # Clear PDF-wise Summaries
        st.session_state["pdf_summaries_by_document"] = {}

        # Clear old/global result keys if they exist
        st.session_state.pop("mcqs", None)
        st.session_state.pop("mcq_submitted", None)
        st.session_state.pop("mcq_score", None)
        st.session_state.pop("mcq_results", None)
        st.session_state.pop("important_questions", None)
        st.session_state.pop("pdf_summary", None)

        st.success(
            "All study results have been cleared."
        )


# =========================================================
# THEME
# =========================================================

if dark_mode:

    background = "#000000"
    text = "#ffffff"
    secondary = "#b5b5b5"
    border = "#2b2b2b"
    card = "#111111"

    button_background = "#ffffff"
    button_text = "#000000"

else:

    background = "#ffffff"
    text = "#000000"
    secondary = "#666666"
    border = "#dddddd"
    card = "#fafafa"

    button_background = "#000000"
    button_text = "#ffffff"


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    f"""
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {{
        background: {background};
        color: {text};
    }}
    
    /* =====================================================
   HIDE DEPLOY BUTTON
   ===================================================== */

div[data-testid="stDeployButton"] {{
    display: none !important;
}}

    body {{
        background: {background};
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {text} !important;
    }}

    p {{
        color: {text};
    }}


    /* =====================================================
       HIDE STREAMLIT DEFAULT UI
       ===================================================== */

    #MainMenu {{
        display: none !important;
    }}

    footer {{
        display: none !important;
    }}

    [data-testid="stDecoration"] {{
        display: none !important;
    }}

    [data-testid="stStatusWidget"] {{
        display: none !important;
    }}


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {{
        background: {background};
        border-right: 1px solid {border};
    }}

    section[data-testid="stSidebar"] h1 {{
        color: {text} !important;
        font-size: 22px;
        font-weight: 700;
    }}

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {text} !important;
    }}

    section[data-testid="stSidebar"] p {{
        color: {secondary} !important;
    }}


    /* =====================================================
       DIVIDERS
       ===================================================== */

    hr {{
        border-color: {border} !important;
    }}


    /* =====================================================
       RADIO BUTTONS
       ===================================================== */

    div[data-testid="stRadio"] label {{
        color: {text} !important;
    }}


    /* =====================================================
       TOGGLE
       ===================================================== */

    div[data-testid="stCheckbox"] label {{
        color: {text} !important;
    }}


    /* =====================================================
       FILE UPLOADER
       ===================================================== */

    [data-testid="stFileUploaderDropzone"] {{
        background: {card} !important;
        border: 1px dashed {border} !important;
        border-radius: 12px !important;
        min-height: 140px;
    }}

    [data-testid="stFileUploaderDropzone"]:hover {{
        border-color: {text} !important;
    }}

    [data-testid="stFileUploaderDropzone"] * {{
        color: {text} !important;
    }}


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {{
        background: {button_background} !important;
        color: {button_text} !important;
        border: 1px solid {button_background} !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        min-height: 40px !important;
    }}

    .stButton > button p {{
        color: {button_text} !important;
    }}

    .stButton > button span {{
        color: {button_text} !important;
    }}

    .stButton > button:hover {{
        opacity: 0.8;
    }}


    /* =====================================================
       FEATURE CARDS
       ===================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {card};
        border: 1px solid {border};
        border-radius: 12px;
    }}


    /* =====================================================
       ALERTS
       ===================================================== */

    div[data-testid="stAlert"] {{
        border-radius: 10px;
    }}


    /* =====================================================
       CAPTIONS
       ===================================================== */

    .stCaption {{
        color: {secondary} !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# MAIN HEADER
# =========================================================

st.title("Learn smarter with your PDFs.")

st.write(
    "Upload your study material and use AI to ask questions, "
    "practice MCQs, prepare for exams, and create summaries."
)

st.divider()


# =========================================================
# PDF UPLOAD
# =========================================================

st.subheader("Upload your study material")

st.caption(
    "PDF files only • You can upload multiple PDFs"
)

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True
)


# =========================================================
# MULTIPLE PDF PROCESSING
# =========================================================

if uploaded_files:

    try:

        pending_documents = []

        for uploaded_file in uploaded_files:

            documents = load_pdf(uploaded_file)

            page_count = len(documents)

            chunks = split_documents(documents)

            pending_documents.append(
                {
                    "file": uploaded_file,
                    "pages": page_count,
                    "chunks": chunks
                }
            )

            st.success(
                f"{uploaded_file.name} • "
                f"{page_count} pages detected"
            )

            st.caption(
                f"{len(chunks)} text chunks created."
            )


        # -------------------------------------------------
        # PROCESS PDFs
        # -------------------------------------------------

        if st.button(
            "Process PDF(s)",
            key="process_pdfs_button",
            use_container_width=True
        ):

            collection = get_vector_store()

            with st.spinner(
                "Processing PDF files..."
            ):

                for document in pending_documents:

                    uploaded_file = document["file"]

                    chunks = document["chunks"]

                    document_id = (
                        Path(
                            uploaded_file.name
                        )
                        .stem
                        .replace(" ", "_")
                        .lower()
                    )

                    existing_documents = collection.get(
                        where={
                            "document_id": document_id
                        },
                        limit=1
                    )


                    # -------------------------------------
                    # PDF ALREADY PROCESSED
                    # -------------------------------------

                    if existing_documents["ids"]:

                        st.info(
                            f"{uploaded_file.name} "
                            f"already processed. Existing data reused."
                        )


                    # -------------------------------------
                    # NEW PDF
                    # -------------------------------------

                    else:

                        embeddings = []

                        for chunk in chunks:

                            embedding = create_embedding(
                                chunk["text"]
                            )

                            embeddings.append(
                                embedding
                            )


                        create_vector_store(
                            chunks,
                            embeddings,
                            document_id
                        )


                    # -------------------------------------
                    # SAVE PDF INFORMATION
                    # -------------------------------------

                    st.session_state[
                        "processed_documents"
                    ][document_id] = {
                        "name": uploaded_file.name,
                        "pages": document["pages"],
                        "chunks": chunks
                    }


                # -----------------------------------------
                # ACTIVE PDF
                # -----------------------------------------

                document_ids = list(
                    st.session_state[
                        "processed_documents"
                    ].keys()
                )

                if document_ids:

                    active_document_id = document_ids[0]

                    active_document = (
                        st.session_state[
                            "processed_documents"
                        ][active_document_id]
                    )

                    st.session_state[
                        "document_id"
                    ] = active_document_id

                    st.session_state[
                        "chunks"
                    ] = active_document["chunks"]

                    st.session_state[
                        "collection"
                    ] = collection

                    st.session_state[
                        "processed"
                    ] = True


            st.success(
                "PDF files processed successfully!"
            )


        # =================================================
        # PDF SELECTION
        # =================================================

        if st.session_state.get(
            "processed_documents"
        ):

            processed_documents = (
                st.session_state[
                    "processed_documents"
                ]
            )

            document_names = {
                document_id: data["name"]
                for document_id, data
                in processed_documents.items()
            }

            document_ids = list(
                document_names.keys()
            )

            current_document_id = (
                st.session_state.get(
                    "document_id"
                )
            )

            if current_document_id not in document_ids:
                current_document_id = document_ids[0]

            current_index = document_ids.index(
                current_document_id
            )

            st.subheader(
                "📄 Select PDF"
            )

            selected_document_name = st.selectbox(
                "Choose which PDF you want to study",
                [
                    document_names[document_id]
                    for document_id in document_ids
                ],
                index=current_index
            )

            selected_document_id = next(
                document_id
                for document_id in document_ids
                if document_names[
                    document_id
                ] == selected_document_name
            )


            # -----------------------------------------
            # UPDATE ACTIVE PDF
            # -----------------------------------------

            if (
                selected_document_id
                != st.session_state.get(
                    "document_id"
                )
            ):

                st.session_state[
                    "document_id"
                ] = selected_document_id

                st.session_state[
                    "chunks"
                ] = processed_documents[
                    selected_document_id
                ]["chunks"]


            selected_pdf = (
                processed_documents[
                    selected_document_id
                ]
            )

            st.success(
                f"Active PDF: {selected_pdf['name']}"
            )


    except Exception as e:

        st.error(
            f"Could not process PDF files: {e}"
        )


# =========================================================
# STUDY TOOLS
# =========================================================

st.divider()

st.subheader("Study tools")

col1, col2, col3, col4 = st.columns(4)


# =========================================================
# ASK AI CARD
# =========================================================

with col1:

    with st.container(border=True):

        st.markdown("### 💬")
        st.markdown("**Ask AI**")
        st.caption(
            "Ask questions directly from your PDF."
        )

        st.button(
            "Open Ask AI",
            key="card_ask_ai",
            use_container_width=True,
            on_click=select_tool,
            args=("💬 Ask AI",)
        )


# =========================================================
# MCQ CARD
# =========================================================

with col2:

    with st.container(border=True):

        st.markdown("### 📝")
        st.markdown("**Generate MCQs**")
        st.caption(
            "Create practice questions from your material."
        )

        st.button(
            "Open MCQs",
            key="card_mcqs",
            use_container_width=True,
            on_click=select_tool,
            args=("📝 Generate MCQs",)
        )


# =========================================================
# IMPORTANT QUESTIONS CARD
# =========================================================

with col3:

    with st.container(border=True):

        st.markdown("### 🎯")
        st.markdown("**Important Questions**")
        st.caption(
            "Find useful questions for exam preparation."
        )

        st.button(
            "Open Important Questions",
            key="card_important",
            use_container_width=True,
            on_click=select_tool,
            args=("🎯 Important Questions",)
        )


# =========================================================
# SUMMARY CARD
# =========================================================

with col4:

    with st.container(border=True):

        st.markdown("### 📖")
        st.markdown("**PDF Summary**")
        st.caption(
            "Turn lengthy material into concise notes."
        )

        st.button(
            "Open Summary",
            key="card_summary",
            use_container_width=True,
            on_click=select_tool,
            args=("📖 PDF Summary",)
        )


# =========================================================
# SELECTED TOOL
# =========================================================

st.divider()

st.subheader(tool)


# =========================================================
# ASK AI
# =========================================================

if tool == "💬 Ask AI":

    if st.session_state.get(
        "processed",
        False
    ):

        st.subheader("Ask a question")

        question = st.text_input(
            "What do you want to know from your PDF?",
            placeholder="Example: What is Amdahl's Law?"
        )

        if st.button(
            "Ask AI",
            key="ask_ai_button",
            use_container_width=True
        ):

            if question.strip():

                with st.spinner(
                    "Searching your PDF..."
                ):

                    query_embedding = create_embedding(
                        question
                    )

                    collection = st.session_state[
                        "collection"
                    ]

                    document_id = st.session_state[
                        "document_id"
                    ]

                    results = search_documents(
                        collection=collection,
                        query_embedding=query_embedding,
                        document_id=document_id,
                        top_k=3
                    )

                retrieved_chunks = (
                    results["documents"][0]
                )

                retrieved_metadata = (
                    results["metadatas"][0]
                )

                context_parts = []

                for chunk, metadata in zip(
                    retrieved_chunks,
                    retrieved_metadata
                ):

                    context_parts.append(
                        f"Page {metadata['page']}:\n{chunk}"
                    )

                context = "\n\n".join(
                    context_parts
                )

                prompt = create_qa_prompt(
                    context,
                    question
                )

                with st.spinner(
                    "Generating answer..."
                ):

                    answer = generate_answer(
                        prompt
                    )

                st.session_state[
                    "ask_ai_history"
                ].append(
                    {
                        "question": question,
                        "answer": answer,
                        "sources": retrieved_metadata,
                        "document_id": document_id
                    }
                )

            else:

                st.warning(
                    "Please enter a question."
                )


        # -------------------------------------------------
        # SHOW HISTORY FOR CURRENT PDF ONLY
        # -------------------------------------------------

        current_document_id = st.session_state.get(
            "document_id"
        )

        ask_history = [
            item
            for item in st.session_state.get(
                "ask_ai_history",
                []
            )
            if item.get(
                "document_id"
            ) == current_document_id
        ]


        if ask_history:

            st.markdown(
                "### 📚 Previous Answers"
            )

            for index, result in enumerate(
                reversed(ask_history),
                start=1
            ):

                st.markdown(
                    f"### Question {index}"
                )

                st.markdown(
                    f"**{result['question']}**"
                )

                st.markdown(
                    "### Answer"
                )

                st.write(
                    result["answer"]
                )

                st.markdown(
                    "### Sources"
                )

                for metadata in result["sources"]:

                    st.caption(
                        f"📄 Page {metadata['page']}"
                    )

                if index < len(ask_history):
                    st.divider()

    else:

        st.info(
            "Upload and process a PDF first."
        )


# =========================================================
# MCQs
# =========================================================

elif tool == "📝 Generate MCQs":

    if st.session_state.get(
        "processed",
        False
    ):

        current_document_id = (
            st.session_state.get(
                "document_id"
            )
        )

        st.subheader(
            "Generate Practice MCQs"
        )

        st.write(
            "Create 10 multiple-choice questions from your PDF."
        )

        # -------------------------------------------------
        # GENERATE MCQs
        # -------------------------------------------------

        if st.button(
            "Generate 10 MCQs",
            key="generate_mcqs_button",
            use_container_width=True
        ):

            chunks_for_tools = st.session_state.get(
                "chunks",
                []
            )

            context = "\n\n".join(
                chunk["text"]
                for chunk in chunks_for_tools
            )

            try:

                with st.spinner(
                    "Generating MCQs from your PDF..."
                ):

                    mcqs = generate_mcqs(
                        context
                    )

                st.session_state[
                    "mcqs_by_document"
                ][current_document_id] = mcqs

                st.session_state[
                    "mcq_submitted_by_document"
                ][current_document_id] = False

                st.session_state[
                    "mcq_score_by_document"
                ].pop(
                    current_document_id,
                    None
                )

                st.session_state[
                    "mcq_results_by_document"
                ].pop(
                    current_document_id,
                    None
                )

            except Exception as e:

                st.error(
                    f"Could not generate MCQs right now: {e}"
                )


        # -------------------------------------------------
        # GET CURRENT PDF MCQs
        # -------------------------------------------------

        current_mcqs = st.session_state[
            "mcqs_by_document"
        ].get(
            current_document_id
        )


        if current_mcqs is not None:

            mcqs = current_mcqs

            st.divider()

            st.subheader(
                "📝 Your Quiz"
            )

            user_answers = []

            for index, mcq in enumerate(
                mcqs.questions
            ):

                st.markdown(
                    f"**Q{index + 1}. {mcq.question}**"
                )

                answer = st.radio(
                    "Choose your answer:",
                    [
                        f"A. {mcq.option_a}",
                        f"B. {mcq.option_b}",
                        f"C. {mcq.option_c}",
                        f"D. {mcq.option_d}",
                    ],
                    key=(
                        f"mcq_{current_document_id}_{index}"
                    ),
                    index=None
                )

                if answer:

                    user_answers.append(
                        answer[0]
                    )

                else:

                    user_answers.append("")


            # -------------------------------------------------
            # SUBMIT QUIZ
            # -------------------------------------------------

            if st.button(
                "Submit Quiz",
                key="submit_quiz_button",
                use_container_width=True
            ):

                if "" in user_answers:

                    st.warning(
                        "Please answer all 10 questions before submitting."
                    )

                else:

                    score, results = check_answers(
                        mcqs,
                        user_answers
                    )

                    st.session_state[
                        "mcq_score_by_document"
                    ][current_document_id] = score

                    st.session_state[
                        "mcq_results_by_document"
                    ][current_document_id] = results

                    st.session_state[
                        "mcq_submitted_by_document"
                    ][current_document_id] = True


            # -------------------------------------------------
            # SHOW SCORE
            # -------------------------------------------------

            if st.session_state[
                "mcq_submitted_by_document"
            ].get(
                current_document_id,
                False
            ):

                score = st.session_state[
                    "mcq_score_by_document"
                ][current_document_id]

                results = st.session_state[
                    "mcq_results_by_document"
                ][current_document_id]

                st.divider()

                st.subheader(
                    f"🎯 Your Score: {score}/10"
                )

                for index, result in enumerate(
                    results
                ):

                    if result["is_correct"]:

                        st.success(
                            f"Q{index + 1}: Correct ✓"
                        )

                    else:

                        st.error(
                            f"Q{index + 1}: "
                            f"Your answer: {result['user_answer']} | "
                            f"Correct answer: {result['correct_answer']}"
                        )

    else:

        st.info(
            "Upload and process a PDF first."
        )


# =========================================================
# IMPORTANT QUESTIONS
# =========================================================

elif tool == "🎯 Important Questions":

    if st.session_state.get(
        "processed",
        False
    ):

        current_document_id = (
            st.session_state.get(
                "document_id"
            )
        )

        st.subheader(
            "❓ Important Exam Questions"
        )

        st.write(
            "Generate 10 important questions from your selected PDF."
        )

        # -------------------------------------------------
        # GENERATE IMPORTANT QUESTIONS
        # -------------------------------------------------

        if st.button(
            "Generate 10 Important Questions",
            key="generate_important_questions_button",
            use_container_width=True
        ):

            chunks_for_tools = st.session_state.get(
                "chunks",
                []
            )

            context = "\n\n".join(
                chunk["text"]
                for chunk in chunks_for_tools
            )

            try:

                with st.spinner(
                    "Generating important questions from your PDF..."
                ):

                    questions = generate_important_questions(
                        context
                    )

                st.session_state[
                    "important_questions_by_document"
                ][current_document_id] = questions

            except Exception as e:

                st.error(
                    f"Could not generate important questions right now: {e}"
                )


        # -------------------------------------------------
        # SHOW CURRENT PDF QUESTIONS
        # -------------------------------------------------

        current_questions = st.session_state[
            "important_questions_by_document"
        ].get(
            current_document_id
        )

        if current_questions is not None:

            st.divider()

            st.subheader(
                "📚 Important Questions"
            )

            for index, question in enumerate(
                current_questions.questions
            ):

                st.markdown(
                    f"**Q{index + 1}. {question}**"
                )

    else:

        st.info(
            "Upload and process a PDF first."
        )


# =========================================================
# PDF SUMMARY
# =========================================================

elif tool == "📖 PDF Summary":

    if st.session_state.get(
        "processed",
        False
    ):

        current_document_id = (
            st.session_state.get(
                "document_id"
            )
        )

        st.subheader(
            "📄 PDF Summary"
        )

        st.write(
            "Generate a concise study summary from your selected PDF."
        )

        # -------------------------------------------------
        # GENERATE SUMMARY
        # -------------------------------------------------

        if st.button(
            "Generate PDF Summary",
            key="generate_summary_button",
            use_container_width=True
        ):

            chunks_for_tools = st.session_state.get(
                "chunks",
                []
            )

            context = "\n\n".join(
                chunk["text"]
                for chunk in chunks_for_tools
            )

            try:

                with st.spinner(
                    "Generating summary from your PDF..."
                ):

                    summary = generate_summary(
                        context
                    )

                st.session_state[
                    "pdf_summaries_by_document"
                ][current_document_id] = summary

            except Exception as e:

                st.error(
                    f"Could not generate summary right now: {e}"
                )


        # -------------------------------------------------
        # SHOW CURRENT PDF SUMMARY
        # -------------------------------------------------

        current_summary = st.session_state[
            "pdf_summaries_by_document"
        ].get(
            current_document_id
        )

        if current_summary:

            st.divider()

            st.subheader(
                "📝 Study Summary"
            )

            st.markdown(
                current_summary
            )

    else:

        st.info(
            "Upload and process a PDF first."
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "DocuMind AI • Built for smarter studying"
)
