Search.setIndex({docnames:["index","modules","monitoring"],envversion:53,filenames:["index.rst","modules.rst","monitoring.rst"],objects:{"":{monitoring:[2,0,0,"-"]},"monitoring.config":{Config:[2,1,1,""]},"monitoring.config.Config":{configure:[2,2,1,""],default_env:[2,3,1,""],getconfig:[2,2,1,""],getconsolidations:[2,2,1,""],getgeneric:[2,2,1,""],getmonitoring:[2,2,1,""],getserver:[2,2,1,""],getstorage:[2,2,1,""],load_json:[2,2,1,""],os_env:[2,3,1,""],providers:[2,3,1,""],secret:[2,3,1,""],services:[2,3,1,""]},"monitoring.consolidation":{Consolidation:[2,1,1,""],ConsolidationSLA:[2,1,1,""],ConsolidationStatus:[2,1,1,""],MongoStorageConsolidationSLA:[2,1,1,""],MongoStorageConsolidationStatus:[2,1,1,""]},"monitoring.consolidation.Consolidation":{run:[2,2,1,""],stopConsolidation:[2,2,1,""]},"monitoring.consolidation.ConsolidationSLA":{compute_daily_sla:[2,2,1,""],compute_monthly_sla:[2,2,1,""],compute_weekly_sla:[2,2,1,""],next_date_daily_sla:[2,2,1,""],next_date_monthly_sla:[2,2,1,""],next_date_weekly_sla:[2,2,1,""],previous_date_daily_sla:[2,2,1,""],previous_date_monthly_sla:[2,2,1,""],previous_date_weekly_sla:[2,2,1,""],run:[2,2,1,""]},"monitoring.consolidation.ConsolidationStatus":{run:[2,2,1,""]},"monitoring.consolidation.MongoStorageConsolidationSLA":{daily_sla_done:[2,2,1,""],hook_daily_sla:[2,2,1,""],hook_monthly_sla:[2,2,1,""],hook_weekly_sla:[2,2,1,""],monthly_sla_done:[2,2,1,""],weekly_sla_done:[2,2,1,""]},"monitoring.consolidation.MongoStorageConsolidationStatus":{compute_status:[2,2,1,""]},"monitoring.helper":{DaemonHelper:[2,1,1,""]},"monitoring.helper.DaemonHelper":{sleep_with_stop_switch:[2,2,1,""]},"monitoring.monitoring":{ServicesMonitoring:[2,1,1,""],TaskMonitoring:[2,1,1,""]},"monitoring.monitoring.ServicesMonitoring":{add:[2,2,1,""],remove:[2,2,1,""],remove_delegation:[2,2,1,""],remove_provider:[2,2,1,""],startMonitoring:[2,2,1,""],stopMonitoring:[2,2,1,""],task_add:[2,2,1,""],task_remove:[2,2,1,""]},"monitoring.monitoring.TaskMonitoring":{add:[2,2,1,""],checkService:[2,2,1,""],isEmpty:[2,2,1,""],remove:[2,2,1,""],run:[2,2,1,""],stopTask:[2,2,1,""]},"monitoring.providers":{IngressProvider:[2,1,1,""],IngressProviderConfig:[2,1,1,""],Provider:[2,1,1,""]},"monitoring.providers.IngressProvider":{dispatch_ingress_event:[2,2,1,""],ingress_event_added:[2,2,1,""],ingress_event_deleted:[2,2,1,""],ingress_event_modified:[2,2,1,""],ingress_event_modified_remove_hook:[2,2,1,""],ingress_event_to_services:[2,2,1,""],ingress_events:[2,2,1,""],restart_timeout:[2,3,1,""],run:[2,2,1,""],stopProvider:[2,2,1,""],watch_timeout_seconds:[2,3,1,""]},"monitoring.providers.IngressProviderConfig":{exclude:[2,2,1,""],headers:[2,2,1,""]},"monitoring.providers.Provider":{run:[2,2,1,""],services_add:[2,2,1,""],services_cleanup:[2,2,1,""],services_remove:[2,2,1,""],services_remove_delegation:[2,2,1,""],stopProvider:[2,2,1,""]},"monitoring.server":{Server:[2,1,1,""]},"monitoring.server.Server":{configure:[2,2,1,""],configure_mongostorage:[2,2,1,""],exit:[2,2,1,""],providers_add:[2,2,1,""],providers_remove_all:[2,2,1,""],running:[2,2,1,""],startMonitoring:[2,2,1,""],stopMonitoring:[2,2,1,""],storage_get_notify:[2,2,1,""],terminate_signal:[2,2,1,""]},"monitoring.services":{ElasticsearchService:[2,1,1,""],IngressService:[2,1,1,""],KubernetesService:[2,1,1,""],MongoService:[2,1,1,""],Service:[2,1,1,""]},"monitoring.services.ElasticsearchService":{checkMe:[2,2,1,""]},"monitoring.services.IngressService":{checkMe:[2,2,1,""],timeout:[2,3,1,""]},"monitoring.services.KubernetesService":{checkMe:[2,2,1,""]},"monitoring.services.MongoService":{checkMe:[2,2,1,""],timeout:[2,3,1,""]},"monitoring.services.Service":{FAIL:[2,3,1,""],OK:[2,3,1,""],checkMe:[2,2,1,""],isHardFailure:[2,2,1,""],isSoftFailure:[2,2,1,""],reset_status:[2,2,1,""],storage_add:[2,2,1,""],storage_get:[2,2,1,""],storage_remove:[2,2,1,""]},"monitoring.storage":{MongoStorage:[2,1,1,""],Storage:[2,1,1,""]},"monitoring.storage.MongoStorage":{isReady:[2,2,1,""],query_exec_end_downtime:[2,2,1,""],query_exec_find_all_downtimes:[2,2,1,""],query_exec_find_current_downtime:[2,2,1,""],query_exec_find_svc:[2,2,1,""],query_exec_find_svc_by_id:[2,2,1,""],query_exec_new_downtime:[2,2,1,""],query_exec_new_svc:[2,2,1,""],stats_get_all_downtimes_svc:[2,2,1,""],stats_get_all_svc:[2,2,1,""],stats_get_svc:[2,2,1,""],storage_id_downtime:[2,3,1,""],storage_id_svc:[2,3,1,""],svc_all:[2,2,1,""],timeout:[2,3,1,""]},"monitoring.storage.Storage":{isReady:[2,2,1,""],stats_day_duration:[2,2,1,""],stats_first_date_of_week_number:[2,2,1,""],stats_get_all_daily_sla:[2,2,1,""],stats_get_all_downtimes:[2,2,1,""],stats_get_all_monthly_sla:[2,2,1,""],stats_get_all_sla:[2,2,1,""],stats_get_all_status:[2,2,1,""],stats_get_all_status_for_ns:[2,2,1,""],stats_get_all_weekly_sla:[2,2,1,""],stats_get_all_yearly_sla:[2,2,1,""],stats_get_svc_daily_sla:[2,2,1,""],stats_get_svc_downtimes:[2,2,1,""],stats_get_svc_monthly_sla:[2,2,1,""],stats_get_svc_sla:[2,2,1,""],stats_get_svc_status:[2,2,1,""],stats_get_svc_weekly_sla:[2,2,1,""],stats_get_svc_yearly_sla:[2,2,1,""],stats_month_duration:[2,2,1,""],stats_week_duration:[2,2,1,""],stats_week_number_of_date:[2,2,1,""],stats_year_duration:[2,2,1,""],svc_all:[2,2,1,""],svc_elasticsearch:[2,2,1,""],svc_ingress:[2,2,1,""],svc_kubernetes:[2,2,1,""],svc_mongo:[2,2,1,""],update_status:[2,2,1,""]},monitoring:{config:[2,0,0,"-"],consolidation:[2,0,0,"-"],helper:[2,0,0,"-"],monitoring:[2,0,0,"-"],providers:[2,0,0,"-"],server:[2,0,0,"-"],services:[2,0,0,"-"],storage:[2,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute"},terms:{"class":2,"default":2,"float":2,"function":2,"int":2,"long":2,"new":2,"return":2,"true":2,"try":2,Added:2,NOT:2,Not:2,That:2,The:2,Use:2,Used:2,Yes:2,__eq__:2,__str__:2,_id:2,_id_uptim:2,_id_uptime_histori:2,about:2,action:2,adapt:2,add:2,address:2,after:2,all:2,alreadi:2,analyz:2,ani:2,answer:2,anyth:2,argument:2,associ:2,attempt:2,attempt_before_status_fail:2,auth:2,authent:2,automat:2,avail:2,avoid:2,backend:2,backend_notifi:2,base:2,becaus:2,befor:2,begin:2,behavior:2,between:2,bool:2,cach:2,calcul:2,call:2,caller:2,can:2,categori:2,chang:2,check:2,check_every_second:2,checkm:2,checkservic:2,clean:2,client1:2,close:2,cloud:2,code:2,collect:2,compagni:2,compon:2,compos:2,comput:2,compute_daily_sla:2,compute_monthly_sla:2,compute_statu:2,compute_weekly_sla:2,config:[0,1],configur:2,configure_mongostorag:2,connect:2,consid:2,consolid:[0,1],consolidationsla:2,consolidationstatu:2,constructor:2,content:[0,1],context:2,control:2,creat:2,creation:2,criteria:2,current:2,custom:2,daemon:2,daemonhelp:2,dai:2,daili:2,daily_sla_don:2,data:2,date:2,date_:2,datetim:2,db_name:2,decid:2,deep:2,def:2,default_env:2,defin:2,delet:2,depend:2,deriv:2,design:2,detail:2,detect:2,dev:2,dict:2,dictionari:2,differ:2,directli:2,dispatch:2,dispatch_ingress_ev:2,displai:2,document:2,doesn:2,don:2,done:2,donotconfig:2,down:2,down_sinc:2,down_start_d:2,down_time_dur:2,downtim:2,durat:2,dure:2,each:2,elasticsearch:2,elasticsearchservic:2,els:2,empti:2,end:2,end_dat:2,enforc:2,enough:2,entri:2,env:2,epoch:2,equal:2,error:2,essenti:2,etc:2,event:2,everi:2,except:2,exclud:2,exist:2,exit:2,expos:2,extra:2,fact:2,fail:2,failur:2,fals:2,fast:2,fast_retry_every_second:2,few:2,field:2,file:2,filenam:2,filter:2,find:2,first:2,fly:2,forc:2,found:2,frame:2,from:2,get:2,getconfig:2,getconsolid:2,getgener:2,getmonitor:2,getserv:2,getstorag:2,global:2,going:2,hard:2,have:2,header:2,helper:[0,1],hook:2,hook_daily_sla:2,hook_monthly_sla:2,hook_weekly_sla:2,host:2,http:2,id_downtim:2,id_svc:2,implement:2,index:0,indic:2,info:2,inform:2,infra:2,ingress:2,ingress_config:2,ingress_ev:2,ingress_event_ad:2,ingress_event_delet:2,ingress_event_modifi:2,ingress_event_modified_remove_hook:2,ingress_event_to_servic:2,ingressprovid:2,ingressproviderconfig:2,ingressservic:2,inherit:2,insert:2,instanc:2,instanti:2,isempti:2,ishardfailur:2,isreadi:2,issoftfailur:2,issu:2,itself:2,json:2,json_fil:2,kei:2,keyword:2,know:2,kook:2,kube:2,kubernet:2,kubernetesservic:2,kweyword:2,last:2,later:2,least:2,like:2,list:2,load:2,load_json:2,local:2,localhost:2,loop:2,main:2,mainli:2,manag:2,master:2,max_servic:2,mean:2,mecan:2,messag:2,minim:2,modifi:2,modul:[0,1],mondai:2,mongo:2,mongodb:2,mongoservic:2,mongostorag:2,mongostorageconsolidationsla:2,mongostorageconsolidationstatu:2,month:2,monthli:2,monthly_sla_don:2,montlhi:2,more:2,msg:2,multipl:2,name:2,namespac:2,need:2,next:2,next_date_daily_sla:2,next_date_monthly_sla:2,next_date_weekly_sla:2,node:2,none:2,notifi:2,num:2,number:2,obj:2,object:2,objectid:2,one:2,ones:2,onli:2,option:2,orchestr:2,os_env:2,other:2,otherwis:2,overrid:2,overriden:2,own:2,packag:[0,1],page:0,paramet:2,pass:2,per:2,percentag:2,period:2,permit:2,ping:2,point:2,polici:2,port:2,possibl:2,previou:2,previous_date_daily_sla:2,previous_date_monthly_sla:2,previous_date_weekly_sla:2,program:2,progress:2,provid:[0,1],providers_add:2,providers_remove_al:2,purpos:2,queri:2,query_exec_end_downtim:2,query_exec_find_all_downtim:2,query_exec_find_current_downtim:2,query_exec_find_svc:2,query_exec_find_svc_by_id:2,query_exec_new_downtim:2,query_exec_new_svc:2,queue:2,quit:2,rais:2,rang:2,raw:2,reach:2,read:2,readeabl:2,readi:2,realli:2,record:2,redond:2,rel:2,remot:2,remov:2,remove_deleg:2,remove_provid:2,repartit:2,replicaset:2,report:2,repres:2,request:2,reset:2,reset_statu:2,respons:2,restart_timeout:2,retri:2,room:2,run:2,safe:2,sart:2,search:0,second:2,secret:2,section:2,see:2,seervic:2,self:2,server:[0,1],servic:[0,1],services_add:2,services_cleanup:2,services_filt:2,services_remov:2,services_remove_deleg:2,servicesmonitor:2,set:2,setup:2,should:2,shutdown:2,signal:2,sinc:2,sla:2,sleep:2,sleep_inc:2,sleep_tim:2,sleep_with_stop_switch:2,socket:2,soft:2,some:2,sourc:2,specif:2,ssl:2,start:2,start_dat:2,startmonitor:2,state:2,stats_day_dur:2,stats_first_date_of_week_numb:2,stats_get_all_daily_sla:2,stats_get_all_downtim:2,stats_get_all_downtimes_svc:2,stats_get_all_monthly_sla:2,stats_get_all_sla:2,stats_get_all_statu:2,stats_get_all_status_for_n:2,stats_get_all_svc:2,stats_get_all_weekly_sla:2,stats_get_all_yearly_sla:2,stats_get_svc:2,stats_get_svc_daily_sla:2,stats_get_svc_downtim:2,stats_get_svc_monthly_sla:2,stats_get_svc_sla:2,stats_get_svc_statu:2,stats_get_svc_weekly_sla:2,stats_get_svc_yearly_sla:2,stats_month_dur:2,stats_week_dur:2,stats_week_number_of_d:2,stats_year_dur:2,statu:2,still:2,stop:2,stop_switch:2,stopconsolid:2,stopmonitor:2,stopprovid:2,stoptask:2,storag:[0,1],storage_:2,storage_add:2,storage_get:2,storage_get_notifi:2,storage_id_downtim:2,storage_id_svc:2,storage_remov:2,store:2,str:2,string:2,sub:2,submodul:[0,1],success:2,superior:2,support:2,svc_:2,svc_all:2,svc_elasticsearch:2,svc_ingress:2,svc_kubernet:2,svc_mongo:2,task:2,task_add:2,task_remov:2,taskmonitor:2,termin:2,terminate_sign:2,than:2,them:2,thi:2,those:2,thread:2,time:2,timeout:2,timestamp:2,tool:2,track:2,transform:2,type:2,undefin:2,uniqu:2,unix:2,updat:2,update_statu:2,uptim:2,uptime_env:2,uptime_histori:2,uri:2,url:2,usag:2,use:2,used:2,useful:2,using:2,valu:2,variabl:2,wai:2,wait:2,waiting_seconds_between_batch:2,wake:2,watch_timeout_second:2,week:2,weekli:2,weekly_sla_don:2,what:2,when:2,where:2,which:2,wip_date_:2,with_consolid:2,work:2,workload:2,yaml:2,year:2,yearli:2,you:2,your:2},titles:["Welcome to monitoring\u2019s documentation!","monitoring","monitoring package"],titleterms:{config:2,consolid:2,content:2,document:0,helper:2,indic:0,modul:2,monitor:[0,1,2],packag:2,provid:2,server:2,servic:2,storag:2,submodul:2,tabl:0,welcom:0}})