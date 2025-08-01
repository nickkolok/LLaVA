import re

NEXT_TAG_RE = re.compile(r'\s*<next/>\s*', flags=re.IGNORECASE)

def _add_text_single(state, text, image, image_process_mode, request: gr.Request):
    logger.info(f"add_text. ip: {request.client.host}. len: {len(text)}")
    if len(text) <= 0 and image is None:
        state.skip_next = True
        return (state, state.to_gradio_chatbot(), "", None) + (no_change_btn,) * 5
    if args.moderate:
        flagged = violates_moderation(text)
        if flagged:
            state.skip_next = True
            return (state, state.to_gradio_chatbot(), moderation_msg, None) + (
                no_change_btn,) * 5

    if image is not None:
        if '<image>' not in text:
            text = text + '\n<image>'
        text = (text, image, image_process_mode)
        if len(state.get_images(return_pil=True)) > 0:
            state = default_conversation.copy()
    state.append_message(state.roles[0], text)
    state.append_message(state.roles[1], None)
    state.skip_next = False
    return (state, state.to_gradio_chatbot(), "", None) + (disable_btn,) * 5


def process_multiple_segments(state, segments, image, image_process_mode,
                              model_selector, temperature, top_p, max_new_tokens,
                              request: gr.Request):
    image_attached = False

    for i, segment in enumerate(segments):
        logger.info(f"Processing segment {i+1}/{len(segments)}. ip: {request.client.host}")

        segment_image = image if (image is not None and not image_attached) else None
        if segment_image is not None:
            image_attached = True

        if segment_image is not None:
            if '<image>' not in segment:
                segment = segment + '\n<image>'
            segment_text = (segment, segment_image, image_process_mode)
        else:
            segment_text = segment

        state.append_message(state.roles[0], segment_text)
        state.append_message(state.roles[1], None)
        state.skip_next = False

        bot_gen = http_bot(state, model_selector, temperature, top_p, max_new_tokens, request)

        try:
            for output in bot_gen:
                yield output
        except Exception as e:
            logger.error(f"Error in processing segment {i+1}: {e}")
            state.messages[-1][-1] = server_error_msg
            yield (state, state.to_gradio_chatbot()) + (disable_btn, disable_btn, disable_btn, enable_btn, enable_btn)
            return

    return


def add_text(state, text, image, image_process_mode, model_selector,
             temperature, top_p, max_new_tokens, request: gr.Request):
    segments = NEXT_TAG_RE.split(text.strip())
    if len(segments) <= 1:
        return _add_text_single(state, text, image, image_process_mode, request)
    else:
        return process_multiple_segments(state, segments, image, image_process_mode,
                                         model_selector, temperature, top_p,
                                         max_new_tokens, request)


def add_text_wrapper(state, text, image, image_process_mode, model_selector,
                     temperature, top_p, max_new_tokens, request: gr.Request):
    result = add_text(state, text, image, image_process_mode, model_selector,
                      temperature, top_p, max_new_tokens, request)
    return result


def build_demo(embed_mode):
    textbox = gr.Textbox(show_label=False, placeholder="Enter text and press ENTER", container=False)
    with gr.Blocks(title="LLaVA", theme=gr.themes.Default(), css=block_css) as demo:
        state = gr.State()

        if not embed_mode:
            gr.Markdown(title_markdown)

        with gr.Row():
            with gr.Column(scale=3):
                with gr.Row(elem_id="model_selector_row"):
                    model_selector = gr.Dropdown(
                        choices=models,
                        value=models[0] if len(models) > 0 else "",
                        interactive=True,
                        show_label=False,
                        container=False)

                imagebox = gr.Image(type="pil")
                image_process_mode = gr.Radio(
                    ["Crop", "Resize", "Pad", "Default"],
                    value="Default",
                    label="Preprocess for non-square image", visible=False)

                cur_dir = os.path.dirname(os.path.abspath(__file__))
                gr.Examples(examples=[
                    [f"{cur_dir}/examples/extreme_ironing.jpg", "What is unusual about this image?"],
                    [f"{cur_dir}/examples/waterview.jpg", "What are the things I should be cautious about when I visit here?"],
                ], inputs=[imagebox, textbox])

                with gr.Accordion("Parameters", open=False) as parameter_row:
                    temperature = gr.Slider(minimum=0.0, maximum=1.0, value=0.0, step=0.1, interactive=True, label="Temperature",)
                    top_p = gr.Slider(minimum=0.0, maximum=1.0, value=0.7, step=0.1, interactive=True, label="Top P",)
                    max_output_tokens = gr.Slider(minimum=0, maximum=1024, value=512, step=64, interactive=True, label="Max output tokens",)

            with gr.Column(scale=8):
                chatbot = gr.Chatbot(elem_id="chatbot", label="LLaVA Chatbot", height=550)
                with gr.Row():
                    with gr.Column(scale=8):
                        textbox.render()
                    with gr.Column(scale=1, min_width=50):
                        submit_btn = gr.Button(value="Send", variant="primary")
                with gr.Row(elem_id="buttons") as button_row:
                    upvote_btn = gr.Button(value="👍  Upvote", interactive=False)
                    downvote_btn = gr.Button(value="👎  Downvote", interactive=False)
                    flag_btn = gr.Button(value="⚠️  Flag", interactive=False)
                    regenerate_btn = gr.Button(value="🔄  Regenerate", interactive=False)
                    undo_btn = gr.Button(value="↩️  Undo", interactive=False)

        if not embed_mode:
            gr.Markdown(tos_markdown)
            gr.Markdown(learn_more_markdown)
        url_params = gr.JSON(visible=False)

        btn_list = [upvote_btn, downvote_btn, flag_btn, regenerate_btn, undo_btn]
        upvote_btn.click(upvote_last_response,
            [state, model_selector], [textbox, upvote_btn, downvote_btn, flag_btn])
        downvote_btn.click(downvote_last_response,
            [state, model_selector], [textbox, upvote_btn, downvote_btn, flag_btn])
        flag_btn.click(flag_last_response,
            [state, model_selector], [textbox, upvote_btn, downvote_btn, flag_btn])
        regenerate_btn.click(regenerate, [state, image_process_mode],
            [state, chatbot, textbox, imagebox] + btn_list).then(
            http_bot, [state, model_selector, temperature, top_p, max_output_tokens],
            [state, chatbot] + btn_list)
        undo_btn.click(undo_last_message, [state], [state, chatbot, textbox, imagebox] + btn_list)

        # Updated event handlers for submit with multi-segment support
        textbox.submit(
            add_text_wrapper,
            inputs=[state, textbox, imagebox, image_process_mode, model_selector, temperature, top_p, max_output_tokens, gr.Request],
            outputs=[state, chatbot, textbox, imagebox] + btn_list
        )

        submit_btn.click(
            add_text_wrapper,
            inputs=[state, textbox, imagebox, image_process_mode, model_selector, temperature, top_p, max_output_tokens, gr.Request],
            outputs=[state, chatbot, textbox, imagebox] + btn_list
        )

        if args.model_list_mode == "once":
            demo.load(load_demo, [url_params], [state, model_selector],
                _js=get_window_url_params)
        elif args.model_list_mode == "reload":
            demo.load(load_demo_refresh_model_list, None, [state, model_selector])
        else:
            raise ValueError(f"Unknown model list mode: {args.model_list_mode}")

    return demo
