"""AP01: HTML -> Text, Codeblöcke entfernen (plan.md 5.3, K8)."""

from sov.text import CODE_PLACEHOLDER, clean_title, split_body


def test_code_blocks_removed_and_counted():
    html = "<p>Hi &amp; <code>x</code> there</p><pre><code>a = 1\nb &lt; 2</code></pre><p>end</p>"
    parts = split_body(html)
    assert parts.text_nocode == "Hi & x there end"
    assert parts.len_nocode == len("Hi & x there end")
    assert parts.n_code_blocks == 1
    assert parts.code == "a = 1\nb < 2"
    assert parts.code_chars == len("a = 1\nb < 2")
    assert parts.text_for_model == f"Hi & x there {CODE_PLACEHOLDER} end"


def test_inline_code_stays_text():
    parts = split_body("<p>Use <code>len()</code> here</p>")
    assert parts.n_code_blocks == 0
    assert parts.text_nocode == "Use len() here"


def test_multiple_blocks_joined_with_blank_line():
    parts = split_body("<pre>a</pre><p>mid</p><pre>b</pre>")
    assert parts.n_code_blocks == 2
    assert parts.code == "a\n\nb"
    assert parts.code_chars == 2
    assert parts.text_nocode == "mid"


def test_whitespace_collapsed():
    parts = split_body("<p>a\n\n   b</p>\n<p>c</p>")
    assert parts.text_nocode == "a b c"


def test_empty_body():
    parts = split_body("")
    assert parts.text_nocode == ""
    assert parts.len_nocode == 0
    assert parts.n_code_blocks == 0


def test_clean_title_unescapes():
    assert clean_title("Why isn&#39;t x &gt; y?") == "Why isn't x > y?"
