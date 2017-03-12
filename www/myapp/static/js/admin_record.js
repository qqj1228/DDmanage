function initVM() {
    var vm = new Vue({
        el: '#vm',
        data: {
            records: {}
        },
        mounted: function () {
            this.set_records()
        },
        methods: {
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
