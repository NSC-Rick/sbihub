"""
ElevenLabs Conversational AI Widget Component
"""
import streamlit.components.v1 as components

def render_elevenlabs_widget(agent_id: str):
    """
    Render the ElevenLabs conversational AI widget.
    Attempts to inject into parent window to avoid iframe restrictions.
    
    Args:
        agent_id: The ElevenLabs agent ID
    """
    html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body style="margin: 0; padding: 0;">
            <script>
                (function() {{
                    try {{
                        // Try to inject into parent window
                        var parentDoc = window.parent.document;
                        
                        // Check if script already loaded
                        if (!parentDoc.querySelector('script[src*="convai-widget-embed"]')) {{
                            // Load the ElevenLabs script
                            var script = parentDoc.createElement('script');
                            script.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed';
                            script.type = 'text/javascript';
                            script.async = true;
                            
                            script.onload = function() {{
                                // Create the widget element
                                if (!parentDoc.querySelector('elevenlabs-convai')) {{
                                    var widget = parentDoc.createElement('elevenlabs-convai');
                                    widget.setAttribute('agent-id', '{agent_id}');
                                    parentDoc.body.appendChild(widget);
                                    console.log('ElevenLabs widget injected successfully');
                                }}
                            }};
                            
                            parentDoc.head.appendChild(script);
                        }} else {{
                            // Script already loaded, just add widget if not present
                            if (!parentDoc.querySelector('elevenlabs-convai')) {{
                                var widget = parentDoc.createElement('elevenlabs-convai');
                                widget.setAttribute('agent-id', '{agent_id}');
                                parentDoc.body.appendChild(widget);
                                console.log('ElevenLabs widget added to existing script');
                            }}
                        }}
                    }} catch (e) {{
                        console.error('Failed to inject ElevenLabs widget:', e);
                        // Fallback: load in iframe
                        var widget = document.createElement('elevenlabs-convai');
                        widget.setAttribute('agent-id', '{agent_id}');
                        document.body.appendChild(widget);
                        
                        var script = document.createElement('script');
                        script.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed';
                        script.type = 'text/javascript';
                        document.head.appendChild(script);
                    }}
                }})();
            </script>
        </body>
        </html>
    """
    
    components.html(html_code, height=0, scrolling=False)
