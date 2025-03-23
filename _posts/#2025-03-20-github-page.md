# GitHub Pages Setting

## 两种产生页面的方式

- Deploy from a branch

  选好 branch 和 folder，folder 里面不需要任何 workflow 文件。

  每次这个 folder 里面的变动被 push 以后，GitHub 自带的 action pages build and deployment 会自动运行，使用 jekyll 产生页面。

  这个 action 的构成如下：

  - build (job)

    - checkout

      actions/checkout@v4

    - build with jekyll

      actions/jekyll-build-pages@v1

    - upload artifact

      actions/upload-pages-artifact@v3（常见）

      actions/upload-artifact@v4（这个不知道干嘛的）

  - deploy (job)

    - actions/deploy-pages@v4（常见）

- GitHub Actions

  - Hugo 例子

    也是用到了 actions/checkout、actions/upload-pages-artifact 和 actions/deploy-pages。

    https://gohugo.io/host-and-deploy/host-on-github-pages/

  - 自己写

    也是要用 actions/checkout、actions/upload-pages-artifact 和 actions/deploy-pages。

## 两种部署页面的方式

- actions/upload-pages-artifact 和 actions/deploy-pages

  页面打包成一个 artifact 压缩包，里面包含了所有网页源文件。不用额外的分支来存储网页源文件。

- peaceiris/actions-gh-pages

  可以把网页源文件 push 到另一个专门存放网页源文件的 branch。

## nojekyll

如果选择 deploy from a branch，选择 main branch，并在 folder 中加入文件 .nojekyll，GitHub 自带的 jekyll action 还是会运行。
