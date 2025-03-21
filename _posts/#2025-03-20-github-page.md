# GitHub Pages Setting

两种方式：

- Deploy from a branch

  选好 branch 和 folder，folder 里面不需要任何 workflow 文件。

  每次这个 folder 里面的变动被 push 以后，GitHub 自带的 action pages build and deployment 会自动运行。

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

    https://gohugo.io/host-and-deploy/host-on-github-pages/
