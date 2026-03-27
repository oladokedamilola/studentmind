from django import template
import re

register = template.Library()

@register.filter
def format_resource_content(value):
    """
    Format resource content with proper HTML structure.
    Converts markdown-like syntax to HTML.
    """
    if not value:
        return ''
    
    # First, handle numbered lists (1. 2. 3. etc.)
    value = re.sub(r'(\d+\.)\s+', r'<li>\1 ', value)
    
    # Handle bullet points (* or -)
    value = re.sub(r'^\*\s+', r'<li>', value, flags=re.MULTILINE)
    value = re.sub(r'^-\s+', r'<li>', value, flags=re.MULTILINE)
    
    # Convert markdown headers (## Title)
    value = re.sub(r'^##\s+(.+)$', r'<h5>\1</h5>', value, flags=re.MULTILINE)
    value = re.sub(r'^###\s+(.+)$', r'<h6>\1</h6>', value, flags=re.MULTILINE)
    
    # Convert bold text (**text**)
    value = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', value)
    
    # Convert italic text (*text*)
    value = re.sub(r'\*(.+?)\*', r'<em>\1</em>', value)
    
    # Convert line breaks to paragraphs
    paragraphs = value.split('\n\n')
    formatted_paragraphs = []
    
    for para in paragraphs:
        if not para.strip():
            continue
        
        # Check if it's a list (contains <li> tags)
        if '<li>' in para:
            # Wrap in <ul> if it's a list
            list_items = re.findall(r'<li>(.*?)(?=</li>|$)', para)
            if list_items:
                list_html = '<ul>' + ''.join([f'<li>{item.strip()}</li>' for item in list_items]) + '</ul>'
                formatted_paragraphs.append(list_html)
            else:
                formatted_paragraphs.append(f'<p>{para}</p>')
        elif para.startswith('<h5>') or para.startswith('<h6>'):
            # Headers - no wrapping in <p>
            formatted_paragraphs.append(para)
        else:
            formatted_paragraphs.append(f'<p>{para}</p>')
    
    return '\n'.join(formatted_paragraphs)


@register.filter
def format_step_by_step(value):
    """
    Special formatting for step-by-step guides.
    """
    if not value:
        return ''
    
    # Look for patterns like "Step 1:" or "1."
    steps = re.findall(r'(?:Step\s+)?(\d+)[\.:]\s*(.+?)(?=(?:Step\s+)?\d+[\.:]|$)', value, re.DOTALL)
    
    if steps:
        html = '<div class="steps-container">'
        for step_num, step_content in steps:
            html += f'''
                <div class="step-item">
                    <div class="step-number">{step_num}</div>
                    <div class="step-content">{step_content.strip()}</div>
                </div>
            '''
        html += '</div>'
        return html
    
    return value