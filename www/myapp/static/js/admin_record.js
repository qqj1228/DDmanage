function initVM() {
    var vm = new Vue({
        el: '#vm',
        data: {
            user: '',
            dwg: '',
            url: '',
            date1: '',
            date2: '',
            records: {}
        },
        mounted: function () {
            this.set_records()
        },
        methods: {
            submit: function (event) {
                var self = this;
                $('#loading').show();
                self.date1 = $('#date1').val();
                self.date2 = $('#date2').val();
                postJSON('/api/records', {
                    user: self.user,
                    dwg: self.dwg,
                    url: self.url,
                    date1: self.date1,
                    date2: self.date2
                }, function(err, res){
                    if(err){
                        return fatal(err);
                    }
                    $('#loading').hide();
                    self.records = res.records;
                });
            },
            set_records: function () {
                var self = this;
                $('#loading').show();
                getJSON('/api/records', function(err, res){
                    if(err){
                        return fatal(err);
                    }
                    $('#loading').hide();
                    self.records = res.records;
                });
            }
        }
    });
}

$(function() {
    initVM();
});
