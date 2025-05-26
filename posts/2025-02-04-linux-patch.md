# Submitting Linux Patch

- git add

- git commit

  subsystem 信息也要包括进去

- git format-patch

  `git format-patch --base=v6.14-rc1 -1 -s`

- style check

  `scripts/checkpatch.pl <patch-file>`

- 确定收件人

  `scripts/get_maintainer.pl <patch-file>`

- git send-email / git imap-send (not recommended)

  ```
  git send-email --to <maintainer@email> --cc <group@email> <yourpatch>`
  ```
