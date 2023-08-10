# How to get along with my blog

## Full Workflow

- Environment

  - Install Ruby through package managers

  - Update Gem itself and Bundler if possible

- Pull blog directory containing `Gemfile` from GitHub

- Run `bundle install` to install gems as per `Gemfile`

  Installed gems and their versions will be stored in `Gemfile.lock`.

- Jekyll use

  - Run `bundle exec jekyll s` to view blog locally

  - Run `bundle exec jekyll clean` to delete generated output

- Run `bundle outdated` to check if there are gems that can be updated

- Run `bundle update --all` to update all gems as per `Gemfile`

  After update, latest gems and their versions will be stored in `Gemfile.lock`.

- Update theme

  After updating theme, use the two steps above to update gems.

  - Add the template as a remote

    `git remote add template https://github.com/cotes2020/chirpy-starter`

  - Fetch template

    `git fetch template`

  - Locate commit in the template

    `git log template/main --oneline`

  - Put the change introduced a particular commit onto local main

    `git cherry-pick <commit-id>`

    (Submodule commit will be updated as well.)

  - Update the file `assets/js/dist/post.min.js` with regrad to tocbot

    Search `tocbot.init` in local chirpy gem directory and locate file.

    Copy the file into correct location in blog directory.

    Replace `tocbot.init({` with `tocbot.init({collapseDepth:3`.

## Ruby 101

- Ruby

  Install Ruby with your system's package manager, for example `apt` and `brew`.

  Upgrade Ruby the same way.

  Do not use installers like `ruby-install` and managers like `chruby` as they complicate things.

- Gem

  Gem comes with Ruby by default.

  https://stdgems.org/

  https://guides.rubygems.org/command-reference

  - Install

    `gem install <gem-name>`

  - Update Gem itself

    `gem update --system`

  - Update other gems

    `gem update <gem-name>`

    `gem cleanup`

  - List outdated

    `gem outdated -r`

  - List installed gems

    `gem list`

  - List files in an installed gem

    `gem contents <gem-name>`

  - List info of a gem

    `gem info <gem-name>`

  - Environment

    `gem environment`

    `gem environment home`: display the file path where gems are installed

    `gem environment path`

- Bundler

  https://bundler.io/v2.4/man/bundle.1.html

  Bundler comes with Ruby by default.

  This gem is called **Bundler**, but the corresponding command line program is called **bundle**.

  - Install dependencies

    `bundle install`

    Bundler and Gem installs gems to the same paths.

  - Update dependencies

    Update all the gems to the latest possible versions that still match the gems listed in the `Gemfile`, ignoring the previously installed gems specified in the `Gemfile.lock`.

    `bundle update --all`

  - Execute command

    `bundle exec <command>`

  - `bundle check`

  - `bundle outdated`

  - `bundle show`

  - `bundle show --paths`

## Chirpy Theme

- Chirpy GitHub

  https://github.com/cotes2020/jekyll-theme-chirpy/tree/production

  `tocbot.init` exists in `_javascript/modules/components/toc.js`

- Chirpy Gem

  `_javascript` directory does not exist in the gem directory.

  `toc.js` is corporated into `assets/js/dist/post.min.js`.

- Jekyll blog

  We create a `assets/js/dist/post.min.js` in our blog directory. This file in blog will **override** the file in gem directory.

  Then, we copy the content of `assets/js/dist/post.min.js` in gem directory to `assets/js/dist/post.min.js` in our blog directory.

  Since we want to keep the toc always **expanded**, we replace `tocbot.init({` with `tocbot.init({collapseDepth:3` in `post.min.js`.
