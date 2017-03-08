function initVM() {
    var vm = new Vue({
        el: '#vm',
        data: {
            users: {},
            roles: {},
            email_cu: '',
            role_cu: ''
        },
        mounted: function () {
            this.set_users()
        },
        methods: {
            set_users: function () {
                var self = this;
                $('#loading').show();
                getJSON('/api/users', function(err, res){
                    if(err){
                        return fatal(err);
                    }
                    $('#loading').hide();
                    self.users = res.users;
                });
                getJSON('/api/roles', function(err, res){
                    if(err){
                        return error(err);
                    }
                    self.roles = res.roles;
                });
            },
            show_edit: function (user) {
                this.email_cu = user.email;
                this.role_cu = user.role_name;
            },
            edit_user: function () {
                var self = this;
                postJSON('/api/edit_user', {
                    email: this.email_cu,
                    role_name: this.role_cu
                }, function(err, res){
                    if (err){
                        return error(err);
                    }
                    self.set_users();
                });
            },
            del_user: function (user) {
                var self = this;
                UIkit.modal.confirm("确定要删除用户: " + user.name + " 吗?删除后不可恢复!", function(){
                    postJSON('/api/del_user', {email: user.email}, function(err, res){
                        if (err){
                            return error(err);
                        }
                        self.set_users();
                    });
                });
            }
        }
    });
}

$(function() {
    initVM();
});
