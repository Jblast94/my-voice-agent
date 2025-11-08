import gradio as gr
import os
from datetime import datetime
from llm_handler import LLMHandler
from memory_manager import MemoryManager
from tool_executor import ToolExecutor
from character_learner import CharacterLearner
from audio_handler import AudioHandler

class ConversationalAgent:
    def __init__(self):
        self.llm_handler = LLMHandler()
        self.memory_manager = MemoryManager()
        self.tool_executor = ToolExecutor()
        self.character_learner = CharacterLearner(self.memory_manager)
        self.audio_handler = AudioHandler()
        self.user_id = os.getenv("USER_NAME", "User")
        self.memory_manager.initialize_user_profile(self.user_id)

    def process_message(self, message, history, use_voice=False):
        if not message or not message.strip():
            return history, ""
        
        try:
            self.memory_manager.store_conversation(self.user_id, message, "user")
            learned_traits = self.character_learner.extract_and_learn(self.user_id, message, "user")
            relevant_memories = self.memory_manager.get_relevant_memories(self.user_id, message, limit=5)
            user_profile = self.memory_manager.get_user_profile(self.user_id)
            context = self._build_context(message, relevant_memories, user_profile)
            tools_needed = self._should_use_tools(message)
            tool_results = ""
            if tools_needed:
                tool_results = self.tool_executor.execute_tools(message)
                if tool_results:
                    context += f"\n\nTool Results:\n{tool_results}"
            
            full_response = ""
            for chunk in self.llm_handler.generate_streaming(context):
                full_response += chunk
            
            self.memory_manager.store_conversation(self.user_id, full_response, "assistant")
            self.character_learner.extract_and_learn(self.user_id, full_response, "assistant")
            
            audio_output = None
            if use_voice and full_response:
                audio_output = self.audio_handler.text_to_speech(full_response)
            
            final_history = history + [[message, full_response]]
            yield final_history, "", audio_output
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            error_history = history + [[message, f"I apologize, but I encountered an error: {str(e)}"]]
            yield error_history, "", None

    def process_voice_input(self, audio, history):
        if audio is None:
            return history, ""
        
        try:
            text = self.audio_handler.speech_to_text(audio)
            if text:
                return history, text
            else:
                return history, ""
        except Exception as e:
            print(f"Error processing voice input: {str(e)}")
            return history, ""

    def _build_context(self, message, memories, user_profile):
        context_parts = []
        system_prompt = os.getenv("SYSTEM_PROMPT", "You are a helpful, friendly AI assistant.")
        context_parts.append(f"System: {system_prompt}")
        
        if user_profile:
            profile_info = f"\n\nUser Profile for {self.user_id}:"
            if user_profile.get('learned_traits'):
                traits = __import__('json').loads(user_profile['learned_traits'])
                if traits.get('interests'):
                    profile_info += f"\nInterests: {', '.join(traits['interests'][:5])}"
                if traits.get('background'):
                    profile_info += f"\nBackground: {traits['background']}"
            context_parts.append(profile_info)
        
        if memories:
            context_parts.append("\n\nRelevant past context:")
            for mem in memories[:3]:
                role = mem['role'].capitalize()
                msg = mem['message'][:200]
                context_parts.append(f"{role}: {msg}")
        
        context_parts.append(f"\n\nCurrent User Message: {message}")
        context_parts.append("\nAssistant:")
        
        return "\n".join(context_parts)

    def _should_use_tools(self, message):
        tool_keywords = ['search', 'find', 'google', 'what is', 'who is', 'calculate', 'compute', 'run', 'execute', 'code', 'add task', 'create task', 'workflow', 'automate']
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in tool_keywords)

    def get_memory_stats(self):
        profile = self.memory_manager.get_user_profile(self.user_id)
        if not profile:
            return "No profile data yet."
        
        stats = [f"**User:** {self.user_id}", f"**Profile Created:** {profile.get('created_at', 'Unknown')}"]
        
        if profile.get('learned_traits'):
            traits = __import__('json').loads(profile['learned_traits'])
            stats.append("\n**Learned Information:**")
            
            if traits.get('interests'):
                stats.append(f"- Interests ({len(traits['interests'])}): {', '.join(traits['interests'][:5])}")
            if traits.get('background'):
                stats.append(f"- Background: {traits['background']}")
            if traits.get('communication_style'):
                stats.append(f"- Communication Style: {traits['communication_style']}")
            
            if traits.get('expertise'):
                stats.append(f"- Expertise Areas: {', '.join(traits['expertise'][:3])}")
        
        stats.append(f"\n**Total Conversations:** {self.memory_manager.get_conversation_count(self.user_id)}")
        return "\n".join(stats)

# --- REPLACE THIS ENTIRE FUNCTION ---
def create_interface():
    """Create and configure the Gradio interface."""
    agent = ConversationalAgent()
    
    with gr.Blocks(title="Personal AI Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🤖 Personal AI Assistant
            
            Your intelligent companion that learns about you over time and helps with various tasks.
            
            **Features:**
            - 💬 Natural conversation with memory
            - 🎤 Voice input and output
            - 🧠 Learns your preferences and interests
            - 🔧 Can search the web, execute code, and trigger workflows
            """
        )
        
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500,
                    show_label=True,
                    avatar_images=(None, "🤖")
                )
                
                with gr.Row():
                    with gr.Column(scale=4):
                        msg_input = gr.Textbox(
                            label="Type your message...",
                            placeholder="Ask me anything...",
                            lines=2,
                            show_label=False
                        )
                    with gr.Column(scale=1):
                        audio_input = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            label="🎤 Voice",
                            show_label=True
                        )
                
                with gr.Row():
                    with gr.Column(scale=4):
                        submit_btn = gr.Button("Send 💬", variant="primary")
                        voice_btn = gr.Button("Send with Voice 🔊")
                    with gr.Column(scale=1):
                        clear_btn = gr.Button("Clear 🗑️")
                
        with gr.Column(scale=1):
            audio_output = gr.Audio(
                label="Voice Response",
                autoplay=True,
                type="numpy"
            )
            
            with gr.Row():
                gr.Markdown("### 📊 Memory Stats")
                stats_display = gr.Markdown("Click 'Refresh Stats' to view", lines=8)
                refresh_btn = gr.Button("Refresh Stats 🔄")
        
        # --- Define the update_stats function here ---
        def update_stats():
            return agent.get_memory_stats()
        
        # --- Define all event handlers ---
        def respond(message, history):
            return agent.process_message(message, history, use_voice=False)
        
        def respond_with_voice(message, history):
            return agent.process_message(message, history, use_voice=True)
        
        def process_audio(audio, history):
            return agent.process_voice_input(audio, history)
        
        def clear_history():
            return [], ""
        
        # --- Correctly wire up events ---
        msg_input.submit(
            respond,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input, audio_output]
        )
        
        submit_btn.click(
            respond,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input, audio_output]
        )
        
        voice_btn.click(
            respond_with_voice,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input, audio_output]
        )
        
        audio_input.change(
            process_audio,
            inputs=[audio_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        clear_btn.click(
            clear_history,
            outputs=[chatbot, msg_input]
        )
        
        # Correctly wire up the stats button
        refresh_btn.click(
            update_stats, # Use the function
            outputs=[stats_display] # To the correct output component
        )
        
        # Load stats on startup
        demo.load(
            update_stats, # Use the function
            outputs=[stats_display] # To the correct output component
        )
    
    return demo

# ... (rest of your file is unchanged)

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )