# Syntax Highlighting of Code Blocks in Markdown

Markdown 文件中的代码块的 syntax highlighting 可能会根据 Markdown 文件所处的环境不一样而有不同的效果。Markdown 文件可能有以下环境。

## GitHub 上渲染的 Markdown

### GitHub 原生支持的 Code Block 语言

| Language | Entry in languages.yml | Info String | Grammar |
| --- | --- | --- | --- |
| c       | C   | `c` | https://github.com/tree-sitter/tree-sitter-c |
| kconfig | N/A | N/A | N/A |
| shell session | ShellSession | `shellsession/.sh-session/sh-session/bash-session/console` | https://github.com/atom/language-shellscript |
| bash script | Shell | `shell/{,.}sh/shell-script/ash/{,.}bash/dash/{,.}ksh/mksh/pdksh/{,.}zsh/rc/envrc/{,.}bats/{,.}cgi/{,.}command/{,.}fcgi/{,.}sh.in/{,.}tmux/{,.}tool/{,.}trigger/{,.}zsh-theme` | https://github.com/atom/language-shellscript |
| zsh script | Shell | `shell/{,.}sh/shell-script/ash/{,.}bash/dash/{,.}ksh/mksh/pdksh/{,.}zsh/rc/envrc/{,.}bats/{,.}cgi/{,.}command/{,.}fcgi/{,.}sh.in/{,.}tmux/{,.}tool/{,.}trigger/{,.}zsh-theme` | https://github.com/atom/language-shellscript |
| javascript | JavaScript | `{,.}javascript/{,.}js/node/{,.}_js/{,.}bones/{,.}cjs/{,.}es/{,.}es6/{,.}frag/{,.}gs/{,.}jake/{,.}jsb/{,.}jscad/{,.}jsfl/{,.}jslib/{,.}jsm/{,.}jspre/{,.}jss/{,.}jsx/{,.}mjs/{,.}njs/{,.}pac/{,.}sjs/{,.}ssjs/{,.}xsjs/{,.}xsjslib/chakra/d8/gjs/nodejs/qjs/rhino/v8/v8-shell` | https://github.com/tree-sitter/tree-sitter-javascript |
| json | JSON | `{,.}json/{,.}JSON-tmLanguage/...` | https://github.com/Nixinova/NovaGrammars |
| jsonc | JSON with Comments| `{,.}jsonc/...` | https://github.com/DecimalTurn/vscode-jsonc-syntax-highlighting |

注意区别 shell session 和 shell script。bash script 和 zsh script 在 `languages.yml` 中对应的 entry 都是 Shell，其他 shell script 比如 powershell fish 有自己的 entry。

#### 如何指定语言

> For each language in [`languages.yml`](https://github.com/github/linguist/blob/master/lib/linguist/languages.yml), you can use as specifiers:
>
> 1.  the language name;
> 2.  any of the language `aliases`;
> 3.  any of the language `interpreters`;
> 4.  any of the file extensions, with or without a leading `.`.
>
> Whitespace must be replaced by dashes, for example, `emacs-lisp` is one specifier for `Emacs Lisp`.
>
> Languages with a `tm_scope: none` entry don't have a grammar defined and won't be highlighted on GitHub.
>
> Source: https://github.com/github/linguist/pull/4271

#### 使用什么规则进行 tokenization

linguist 使用语言对应的 grammar 对 Markdown 文件中的 code block 进行 tokenization。

语言对应的 grammar 在 https://github.com/github-linguist/linguist/tree/main/vendor。

### 增加 Code Block 种类

给 linguist 上游提 PR。

## VS Code 编辑器中渲染的 Markdown

参考链接如下：

https://stackoverflow.com/q/68385897/14067245

https://markdown-all-in-one.github.io/docs/guide/syntax-highlighting-for-fenced-code-blocks.html#in-editor

https://github.com/mjbvz/vscode-fenced-code-block-grammar-injection-example

Markdown 插件 GitHub 仓库：https://github.com/microsoft/vscode/blob/main/extensions/markdown-basics。

Markdown 插件本地路径：`/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/extensions/markdown-basics`。

### Syntax Highlighting 原理

Syntax Highlighting 分两步：tokenization 和 theming，具体见 https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide。

Tokenization：VS Code 本身对所有代码文件使用 TextMate grammar 进行 tokenization，Markdown 文件也不例外。VS Code 提供 Markdown 基本支持的插件，定义了针对 Markdown 的 TextMate grammar，常见的 Markdown 结构都在其中进行了定义，具体见 `markdown-basics/syntaxes/markdown.tmLanguage.json`，节选如下：

``` json
"fenced_code_block_c": {
    "begin": "(^|\\G)(\\s*)(`{3,}|~{3,})\\s*(?i:(c|h)((\\s+|:|,|\\{|\\?)[^`]*)?$)",
    "endCaptures": {
        "3": {
            "name": "punctuation.definition.markdown"
        }
    },
    "end": "(^|\\G)(\\2|\\s{0,3})(\\3)\\s*$",
    "patterns": [
        {
            "begin": "(^|\\G)(\\s*)(.*)",
            "patterns": [
                {
                    "include": "source.c"
                }
            ],
            "contentName": "meta.embedded.block.c",
            "while": "(^|\\G)(?!\\s*([`~]{3,})\\s*$)"
        }
    ],
    "name": "markup.fenced_code.block.markdown",
    "beginCaptures": {
        "3": {
            "name": "punctuation.definition.markdown"
        },
        "4": {
            "name": "fenced_code.block.language.markdown"
        },
        "5": {
            "name": "fenced_code.block.language.attributes.markdown"
        }
    }
},
```

Theming：对一个代码文件进行 tokenization 以后，这个代码文件所有的 token 都会有对应的 scope。每个 theme 中都会定义一些 scope 到颜色的映射。比如：

``` js
{
  "scope": "entity.name.function",
  "settings": {
    foreground: lightDark(scale.purple[5], scale.purple[2])
  }
},
```

### VS Code 原生支持的 Code Block

| Language | Entry in markdown.tmLanguage.json | Info String |
| --- | --- | --- |
| c       | fenced_code_block_c | `c/h` |
| kconfig | N/A | N/A |
| shell session | N/A | N/A |
| bash script | fenced_code_block_shell | `shell/sh/bash/zsh/bashrc/bash_profile/bash_login/profile/bash_logout/.textmate_init/\\{\\.bash.+?\\}` |
| zsh script | fenced_code_block_shell | `shell/sh/bash/zsh/bashrc/bash_profile/bash_login/profile/bash_logout/.textmate_init/\\{\\.bash.+?\\}` |
| javascript | fenced_code_block_js | `js/jsx/javascript/es6/mjs/cjs/dataviewjs/\\{\\.js.+?\\}` |
| json | fenced_code_block_json | `json/json5/sublime-settings/sublime-menu/sublime-keymap/sublime-mousemap/sublime-theme/sublime-build/sublime-project/sublime-completions` |
| jsonc | fenced_code_block_jsonc | `jsonc` |

注意，VS Code 只支持对 shell script 进行高亮，不支持对 shell session 进行高亮。

#### 种类

在 `/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/extensions/markdown-basics/syntaxes/markdown.tmLanguage.json` 其中搜索 `fenced_code_block`，可以得到 62 个结果，如下所示。如何指定语言需要去文件中查看。

```
abap
basic
bibtex
c
clojure
coffee
cpp
csharp
css
dart
diff
dockerfile
dosbatch
elixir
erlang
fsharp
git_commit
git_rebase
go
groovy
handlebars
ignore
ini
java
js
js_regexp
json
jsonc
jsonl
julia
latex
less
log
lua
makefile
markdown
objc
perl
perl6
php
powershell
pug
python
r
regexp_python
restructuredtext
ruby
rust
scala
scss
shell
sql
swift
ts
tsx
twig
unknown
vs_net
xml
xsl
yaml
yang
```

#### 如何支持：提供 Grammar

我们在 TextMate grammar 中选择 shell code block 进行分析。其他的 code block 结构类似。

`begin` 匹配 code block 开头 `` ```shell ``。`end` 匹配 code block 结尾 `` ``` ``。code block 开头结尾以及中间的所有内容会被分配 scope `name`，即 `markup.fenced_code.block.markdown`。

`beginCaptures` `endCaptures` 会给 code block 开头和结尾对应的字符分配各自的 scope。

`patterns` 匹配 code block 除去开头和结尾的中间内容。`begin` 对中间内容的每一行进行匹配，`while` 对中间内容的下一行进行匹配，只要没到 code block 结尾，一直进行匹配。分配 scope 使用的规则来自 `source.shell`。`source.shell` 在 https://github.com/microsoft/vscode/blob/main/extensions/shellscript/syntaxes/shell-unix-bash.tmLanguage.json 中定义。

``` json
"fenced_code_block_shell": {
    "name": "markup.fenced_code.block.markdown",
    "begin": "(^|\\G)(\\s*)(`{3,}|~{3,})\\s*(?i:(shell|sh|bash|zsh|bashrc|bash_profile|bash_login|profile|bash_logout|.textmate_init|\\{\\.bash.+?\\})((\\s+|:|,|\\{|\\?)[^`]*)?$)",
    "beginCaptures": {
        "3": {
            "name": "punctuation.definition.markdown"
        },
        "4": {
            "name": "fenced_code.block.language.markdown"
        },
        "5": {
            "name": "fenced_code.block.language.attributes.markdown"
        }
    },
    "end": "(^|\\G)(\\2|\\s{0,3})(\\3)\\s*$",
    "endCaptures": {
        "3": {
            "name": "punctuation.definition.markdown"
        }
    },
    "patterns": [
        {
            "begin": "(^|\\G)(\\s*)(.*)",
            "while": "(^|\\G)(?!\\s*([`~]{3,})\\s*$)",
            "patterns": [
                {
                    "include": "source.shell"
                }
            ],
            "contentName": "meta.embedded.block.shellscript",
        }
    ],
},
```

#### 如何支持：设置 Embedded Languages

Markdown 文件中可能会包含很多其他语言的代码块。https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide#embedded-languages 中指出，如果我们要 VS Code 在编辑 Markdown 文件时对这些其他语言提供完善支持，比如 bracket matching、commenting、snippets。我们需要在 Markdown 插件 `package.json` 的 `contributes.grammars.embeddedLanguages` 中进行设置。

VS Code Markdown 插件的 `package.json` 相关部分如下。`source.js` `source.css` 主要处理直接在 Markdown 中使用 `<style></style>` `<script></script>` 的情况。`embeddedLanguages` 中的这些 key 都是 TextMate grammar 中定义的。比如 `meta.embedded.block.shellscript` 在 `"contentName": "meta.embedded.block.shellscript"` 中定义。

需要注意的是，如果只需要 syntax highlighting，不需要 bracket matching、commenting、snippets，`embeddedLanguages` 可以不用设置。上一小节 62 种语言就有一些没有设置 `embeddedLanguages`。

``` json
    "grammars": [
      {
        "language": "markdown",
        "scopeName": "text.html.markdown",
        "path": "./syntaxes/markdown.tmLanguage.json",
        "embeddedLanguages": {
          "meta.embedded.block.html": "html",
          "source.js": "javascript",
          "source.css": "css",
          "meta.embedded.block.frontmatter": "yaml",
          "meta.embedded.block.css": "css",
          "meta.embedded.block.ini": "ini",
          "meta.embedded.block.java": "java",
          "meta.embedded.block.lua": "lua",
          "meta.embedded.block.makefile": "makefile",
          "meta.embedded.block.perl": "perl",
          "meta.embedded.block.r": "r",
          "meta.embedded.block.ruby": "ruby",
          "meta.embedded.block.php": "php",
          "meta.embedded.block.sql": "sql",
          "meta.embedded.block.vs_net": "vs_net",
          "meta.embedded.block.xml": "xml",
          "meta.embedded.block.xsl": "xsl",
          "meta.embedded.block.yaml": "yaml",
          "meta.embedded.block.dosbatch": "dosbatch",
          "meta.embedded.block.clojure": "clojure",
          "meta.embedded.block.coffee": "coffee",
          "meta.embedded.block.c": "c",
          "meta.embedded.block.cpp": "cpp",
          "meta.embedded.block.diff": "diff",
          "meta.embedded.block.dockerfile": "dockerfile",
          "meta.embedded.block.go": "go",
          "meta.embedded.block.groovy": "groovy",
          "meta.embedded.block.pug": "jade",
          "meta.embedded.block.ignore": "ignore",
          "meta.embedded.block.javascript": "javascript",
          "meta.embedded.block.json": "json",
          "meta.embedded.block.jsonc": "jsonc",
          "meta.embedded.block.jsonl": "jsonl",
          "meta.embedded.block.latex": "latex",
          "meta.embedded.block.less": "less",
          "meta.embedded.block.objc": "objc",
          "meta.embedded.block.scss": "scss",
          "meta.embedded.block.perl6": "perl6",
          "meta.embedded.block.powershell": "powershell",
          "meta.embedded.block.python": "python",
          "meta.embedded.block.restructuredtext": "restructuredtext",
          "meta.embedded.block.rust": "rust",
          "meta.embedded.block.scala": "scala",
          "meta.embedded.block.shellscript": "shellscript",
          "meta.embedded.block.typescript": "typescript",
          "meta.embedded.block.typescriptreact": "typescriptreact",
          "meta.embedded.block.csharp": "csharp",
          "meta.embedded.block.fsharp": "fsharp"
        },
```

### 增加 Code Block 种类

参考 https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide#injection-grammars 和 https://github.com/mjbvz/vscode-fenced-code-block-grammar-injection-example。

如果我们要给 VS Code 编辑器中的 Markdown 文件增加 Code Block 语言支持，我们可以自己创建一个插件，用 injection 的方式添加支持。我们同样需要进行两步：提供语言的 Grammar，设置 Embedded Languages。

其中语言的 Grammar 可以由别的语言插件提供，也可以自己写。

对于 Embedded Languages，如果该语言没有插件支持，设置了也没有作用。

``` jsonc
// package.json
{
  "contributes": {
    "grammars": [
      {
        "path": "./syntaxes/injection.json",
        "scopeName": "injection", // 可以随便取
        "injectTo": ["text.html.markdown"],
        "embeddedLanguages": {
          "meta.embedded.block.kconfig": "kconfig"
        }
      }
    ]
  }
}

// injection.json

{
  "scopeName": "injection", // 要和上面保持一致
  "injectionSelector": "L:text.html.markdown",
  "patterns": [
    {
      "include": "#kconfig-code-block"
    }
  ],
  "repository": {
    "kconfig-code-block": {
      "begin": "(^|\\G)(\\s*)(\\`{3,}|~{3,})\\s*(?i:(kconfig)(\\s+[^`~]*)?$)",
      "name": "markup.fenced_code.block.markdown",
      "end": "(^|\\G)(\\2|\\s{0,3})(\\3)\\s*$",
      "beginCaptures": {
        "3": {
          "name": "punctuation.definition.markdown"
        },
        "4": {
          "name": "fenced_code.block.language.markdown"
        },
        "5": {
          "name": "fenced_code.block.language.attributes.markdown"
        }
      },
      "endCaptures": {
        "3": {
          "name": "punctuation.definition.markdown"
        }
      },
      "patterns": [
        {
          "begin": "(^|\\G)(\\s*)(.*)",
          "while": "(^|\\G)(?!\\s*([`~]{3,})\\s*$)",
          "contentName": "meta.embedded.block.kconfig",
          "patterns": [
            {
              "include": "source.kconfig" // 其他插件有提供的话直接 include，不然要自己写
            }
          ]
        }
      ]
    }
  },
}
```
