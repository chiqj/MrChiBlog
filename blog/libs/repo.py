# coding=utf-8

import os
import hmac

from git import Repo


class PostRepo:
    def __init__(self, repo_dir, ssh_key, repo_branch=None):
        repo_branch = repo_branch or 'master'
        ssh_key = os.path.abspath(ssh_key)
        self.repo = Repo(repo_dir)
        with self.repo.git.custom_environment(GIT_SSH_COMMAND=f"ssh -i {ssh_key}"):
            self.repo.remote().pull(f"{repo_branch}:{repo_branch}")
        self.branch = self.repo.branches[repo_branch]
        self.commit_sha = self.branch.commit
        self.post_exts = ['.md', ]

    def get_all_posts(self):
        """ 获取所有文章 blob 对象列表 """
        trees_list = [self.commit_sha.tree]
        updated_blobs = set()
        removed_blobs = set()

        # 遍历获得所有 blob
        while trees_list:
            tree = trees_list.pop()
            trees_list.extend(tree.trees)
            for blob in tree.blobs:
                # 过滤指定扩展名
                if os.path.splitext(blob.path)[1] in self.post_exts:
                    updated_blobs.add(blob)
        return updated_blobs, removed_blobs

    def get_diff_posts(self, ref, before_sha, after_sha):
        """ 获取更新文章 blob 对象列表 """
        updated_blobs = set()
        removed_blobs = set()
        # 如果不是当前分支的改动，忽略
        if self.branch.path != ref:
            return updated_blobs, removed_blobs

        before_commit = self.repo.commit(before_sha)
        after_commit = self.repo.commit(after_sha)
        for diff in before_commit.diff(after_commit):
            if diff.deleted_file:
                removed_blobs.add(diff.a_blob)
            elif diff.renamed_file:
                updated_blobs.add(diff.b_blob)
                removed_blobs.add(diff.a_blob)
            else:
                updated_blobs.add(diff.b_blob)
        return updated_blobs, removed_blobs

    def get_post_detail(self, blob):
        """ 获取文章详情 """
        # 获取该 blob 的 commit 记录，返回一个逆序的生成器
        commit_generator = self.repo.iter_commits(self.commit_sha, paths=blob.path)
        commit = next(commit_generator)
        last_commit = commit
        for commit in commit_generator:
            pass
        first_commit = commit

        return {
            "title": os.path.splitext(blob.name)[0],
            "content": blob.data_stream.read().decode(),
            "author": {
                "name": last_commit.committer.name,
                "email": last_commit.committer.email,
            },
            "create_time": first_commit.committed_datetime,
            "update_time": last_commit.committed_datetime,
        }


class WebhookSignature:
    @classmethod
    def calc_coding_signature(cls, token, request_data, signature):
        """
        验证 Coding webhook 的签名。

        :param token: 在创建 webhook 时填写的令牌。
        :param request_data: webhook POST 请求内容，可以传入 bytes 或者 str 类型。
        :param signature: webhook POST 请求头中 X-Coding-Signature 字段，通过
        HMAC SHA1 加密算法、使用令牌作为 KEY 将发送内容加密后的值以十六进制显示（需要配置令牌）,并包含前缀 sha1=
        :returns: 签名验证通过返回True，否则返回False。
        """
        if isinstance(token, str):
            token = token.encode()
        if isinstance(request_data, str):
            request_data = request_data.encode()
        if isinstance(signature, bytes):
            signature = signature.decode()
        if signature.startswith("sha1="):
            signature = signature[5:]
        return signature == hmac.new(token, request_data, "sha1").hexdigest()

    @classmethod
    def calc_github_signature(cls, token, request_data, signature):
        """
        验证 GitHub webhook 的签名。

        :param token: 在创建 webhook 时填写的令牌。
        :param request_data: webhook POST 请求内容，可以传入 bytes 或者 str 类型。
        :param signature: webhook POST 请求头中 X-Hub-Signature 字段，通过
        HMAC SHA1 加密算法、使用令牌作为 KEY 将发送内容加密后的值以十六进制显示（需要配置令牌）,并包含前缀 sha1=
        :returns: 签名验证通过返回True，否则返回False。
        """
        if isinstance(token, str):
            token = token.encode()
        if isinstance(request_data, str):
            request_data = request_data.encode()
        if isinstance(signature, bytes):
            signature = signature.decode()
        if signature.startswith("sha1="):
            signature = signature[5:]
        return signature == hmac.new(token, request_data, "sha1").hexdigest()
