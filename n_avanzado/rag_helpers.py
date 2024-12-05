import os
import vertexai
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from vertexai.preview.generative_models import GenerativeModel
from arxiv import Search, SortCriterion
from models_helpers import PLATFORM_CONSTRAINTS, LANGUAGES, language_instructions

SCIENTIFIC_TOPICS = {
    "Physics": "Latest developments in physics research",
    "Mathematics": "Advanced mathematical theories and applications",
    "Computer Science": "Cutting-edge computer science innovations",
    "Biology": "Recent breakthroughs in biological sciences",
    "Finance": "Advanced financial research and economic modeling",
    "Statistics": "Statistical methods and data analysis techniques",
    "Electrical Engineering": "Innovations in electrical and electronic engineering",
    "Systems Science": "Complex systems theory and applications",
    "Economics": "Economic theories and global economic trends"
}

PUBLIC_CONTEXT = {
    "FirstGrader": {
        "description": "Explain complex scientific concepts using very simple language, short sentences, and child-friendly analogies",
        "complexity": 1,
        "style": "Use extremely simple words. Compare complex ideas to everyday objects or experiences that a 6-7 year old would understand. Use playful and engaging language.",
        "example_prefix": "Imagine science is like a big playground where..."
    },
    "MiddleSchooler": {
        "description": "Explain scientific concepts with basic scientific terminology, clear metaphors, and some technical context",
        "complexity": 3,
        "style": "Use age-appropriate scientific vocabulary. Break down complex ideas into manageable steps. Use relatable examples from their daily life or school experiences.",
        "example_prefix": "Let's explore how this scientific concept works, just like we learn about things in science class..."
    },
    "HighSchooler": {
        "description": "Provide more detailed scientific explanations with technical terms, basic mathematical concepts, and deeper conceptual understanding",
        "complexity": 5,
        "style": "Use more advanced scientific terminology. Include basic theoretical frameworks. Explain the underlying principles and mechanisms with some depth.",
        "example_prefix": "To understand this concept, we'll dive into the fundamental principles that drive..."
    },
    "NonExpert": {
        "description": "Create explanations that are accessible, engaging, and informative without assuming prior specialized knowledge",
        "complexity": 4,
        "style": "Avoid jargon. Use clear, conversational language. Provide context and real-world applications. Use analogies and storytelling to make complex ideas digestible.",
        "example_prefix": "Let me break down this scientific concept in a way that makes sense for everyone..."
    },
    "GeneralPublic": {
        "description": "Craft explanations that are broadly accessible, interesting, and capture the wonder of scientific discovery",
        "complexity": 3,
        "style": "Balance technical accuracy with storytelling. Highlight the 'wow' factor. Use inclusive language that invites curiosity.",
        "example_prefix": "Imagine a world where science reveals incredible secrets..."
    }
}

def create_retrieval_system(documents):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    document_texts = [
        str(doc.get('content', '')) for doc in documents 
        if doc.get('content')
    ]
    
    if not document_texts:
        raise ValueError("No valid documents found for retrieval system")
    
    faiss_index = FAISS.from_texts(document_texts, embeddings)
    return faiss_index

def fetch_relevant_documents(topic, max_results=5):
    search = Search(
        query=topic,
        max_results=max_results,
        sort_by=SortCriterion.Relevance 
    )
    
    return [
        {"content": result.summary} 
        for result in search.results() 
        if result.summary
    ]

def retrieve_and_generate(
    query, 
    retrieval_system, 
    content_type='ScientificArticle', 
    language='English',
    public_level='NonExpert',
    topic=None,
    max_results=3
):
    try:
        if not isinstance(query, str):
            query = str(query)
        
        relevant_docs = retrieval_system.similarity_search(query, k=max_results)
        
        retrieved_text = " ".join([
            doc.page_content for doc in relevant_docs 
            if hasattr(doc, 'page_content')
        ])
    
        vertexai.init(project=os.getenv("VERTEX_PROJECT_ID", ""), location="europe-west4")
        
        platform_config = PLATFORM_CONSTRAINTS.get(content_type, PLATFORM_CONSTRAINTS['ScientificArticle'])
        max_chars = platform_config.get('max_chars', 15000)
        prefix = platform_config.get('prefix', 'Generate an informative summary')
        
        language_instruction = language_instructions.get(
            language, 
            f"Write a clear and engaging summary in {language}."
        )
        language_instruction = language_instruction.format(platform=content_type)
        
        model = GenerativeModel(model_name="gemini-1.5-pro-002")
        public_context = PUBLIC_CONTEXT.get(public_level, PUBLIC_CONTEXT['GeneralPublic'])

        prompt = f"""{public_context['example_prefix']}

        Scientific Topic: {topic}
        Target Audience: {public_level}

        Instructions:
        - {public_context['description']}
        - Complexity Level: {public_context['complexity']}/5
        - Writing Style: {public_context['style']}

        Context Documents: {retrieved_text}

        Generate a summary that:
        - Is engaging and accessible
        - Follows the specified writing style
        - Explains key scientific insights in a clear, captivating manner
        - Fits within {max_chars} characters
        """
        
        response = model.generate_content([prompt])

        generated_text = response.text if response and response.text else "Could not generate a summary."
        return generated_text[:max_chars]
    
    except Exception as e:
        return f"An error occurred during content generation: {str(e)}"