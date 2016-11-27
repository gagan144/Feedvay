Search.setIndex({envversion:49,filenames:["index","modules/accounts/exceptions","modules/accounts/forms","modules/accounts/index","modules/accounts/mod_password_recovery","modules/accounts/mod_registration","modules/accounts/mod_sessions","modules/accounts/mod_user_login","modules/accounts/models","modules/accounts/utils","modules/accounts/views","modules/brands/api","modules/brands/forms","modules/brands/index","modules/brands/models","modules/brands/operations","modules/console/context_processors","modules/console/index","modules/console/middleware","modules/console/views","modules/main/index","modules/main/mod_theme","modules/main/views","modules/management_commands/accounts","modules/management_commands/feedvay","modules/management_commands/index","modules/owlery/index","modules/owlery/models","modules/owlery/owls","modules/utilities/api_utils","modules/utilities/aws","modules/utilities/custom_storages","modules/utilities/decorators","modules/utilities/index","modules/utilities/theme","modules/utilities/validators","modules/watchdog/index","modules/watchdog/middleware","modules/watchdog/models"],objects:{"accounts.exceptions":{InvalidRegisteredUser:[1,1,1,""]},"accounts.forms":{BasicInfoForm:[2,2,1,""],PasswordChangeForm:[2,2,1,""],PasswordResetForm:[2,2,1,""],PrivateInfoForm:[2,2,1,""],RegistrationForm:[2,2,1,""]},"accounts.forms.BasicInfoForm":{save:[2,3,1,""]},"accounts.forms.PrivateInfoForm":{save:[2,3,1,""]},"accounts.forms.RegistrationForm":{get_date_of_birth:[2,3,1,""]},"accounts.management.commands.accounts_clear_user_tokens":{Command:[23,2,1,""]},"accounts.models":{RegisteredUser:[8,2,1,""],UserClaim:[8,2,1,""],UserProfile:[8,2,1,""],UserSession:[8,2,1,""],UserToken:[8,2,1,""],force_logout_user:[8,6,1,""],user_logged_in_handler:[8,6,1,""],user_logged_out_handler:[8,6,1,""]},"accounts.models.RegisteredUser":{clean:[8,3,1,""],construct_username:[8,4,1,""],post_save:[8,5,1,""],save:[8,3,1,""],set_password:[8,3,1,""],trans_registered:[8,3,1,""],trans_verification_completed:[8,3,1,""]},"accounts.models.UserClaim":{clean:[8,3,1,""],save:[8,3,1,""],trans_approved:[8,3,1,""],trans_disapproved:[8,3,1,""]},"accounts.models.UserProfile":{DetailedAttribute:[8,2,1,""],UserAttributes:[8,2,1,""],add_update_attribute:[8,3,1,""],delete_attribute:[8,3,1,""],get_meta_dict:[8,3,1,""],lock_attribute:[8,3,1,""],save:[8,3,1,""],unlock_attribute:[8,3,1,""]},"accounts.models.UserToken":{clean:[8,3,1,""],save:[8,3,1,""],verify_user_token:[8,4,1,""]},"accounts.utils":{ClassifyRegisteredUser:[9,2,1,""]},"accounts.views":{login:[10,6,1,""],logout:[10,6,1,""],recover_account:[10,6,1,""],registration:[10,6,1,""],registration_closed:[10,6,1,""],registration_resend_code:[10,6,1,""],registration_verify:[10,6,1,""],reset_password_plea:[10,6,1,""],reset_password_plea_verify:[10,6,1,""]},"brands.api":{BrandChangeRequestAPI:[11,2,1,""],BrandExistenceAPI:[11,2,1,""]},"brands.forms":{BrandCreateEditForm:[12,2,1,""]},"brands.models":{Brand:[14,2,1,""],BrandChangeRequest:[14,2,1,""],BrandOwner:[14,2,1,""]},"brands.models.Brand":{add_owner:[14,3,1,""],clean:[14,3,1,""],delete_owner:[14,3,1,""],does_exists:[14,4,1,""],generate_uitheme:[14,4,1,""],save:[14,3,1,""],trans_delete:[14,3,1,""],trans_revise_verification:[14,3,1,""],trans_verification_failed:[14,3,1,""],trans_verified:[14,3,1,""],update_theme_files:[14,3,1,""],validate_icon_image:[14,4,1,""],validate_logo_image:[14,4,1,""]},"brands.models.BrandChangeRequest":{clean:[14,3,1,""],save:[14,3,1,""]},"brands.models.BrandOwner":{clean:[14,3,1,""],save:[14,3,1,""]},"brands.operations":{create_brand_change_log:[15,6,1,""],create_new_brand:[15,6,1,""],reregister_or_update_brand:[15,6,1,""]},"console.context_processors":{console:[16,6,1,""]},"console.middleware":{ConsoleBrandSwitchMiddleware:[18,2,1,""]},"feedvay.management.commands.feedvay_update_theme_skins":{Command:[24,2,1,""]},"feedvay.views":{docs:[22,6,1,""]},"owlery.models":{EmailMessage:[27,2,1,""],NotificationMessage:[27,2,1,""],NotificationRecipient:[27,2,1,""],SmsMessage:[27,2,1,""],validate_sms_no:[27,6,1,""]},"owlery.models.EmailMessage":{clean:[27,3,1,""],force_send:[27,3,1,""],mark_send:[27,3,1,""],save:[27,3,1,""]},"owlery.models.NotificationMessage":{clean:[27,3,1,""],save:[27,3,1,""]},"owlery.models.NotificationRecipient":{clean:[27,3,1,""],save:[27,3,1,""]},"owlery.models.SmsMessage":{clean:[27,3,1,""],mark_send:[27,3,1,""],save:[27,3,1,""]},"owlery.owls":{EmailOwl:[28,2,1,""],NotificationOwl:[28,2,1,""],SmsOwl:[28,2,1,""]},"owlery.owls.EmailOwl":{send_brand_change_request:[28,4,1,""],send_brand_disassociation_success:[28,4,1,""],send_brand_partner_left_message:[28,4,1,""],send_password_change_success:[28,4,1,""],send_password_reset:[28,4,1,""]},"owlery.owls.NotificationOwl":{send_brand_partner_left_notif:[28,4,1,""]},"owlery.owls.SmsOwl":{send_brand_disassociation_success:[28,4,1,""],send_password_change_success:[28,4,1,""],send_password_reset:[28,4,1,""],send_reg_verification:[28,4,1,""]},"utilities.api_utils":{ApiResponse:[29,2,1,""]},"utilities.api_utils.ApiResponse":{change_status:[29,3,1,""],gen_http_response:[29,3,1,""],set:[29,3,1,""]},"utilities.aws":{upload_to_s3:[30,6,1,""]},"utilities.custom_storages":{MediaStorage:[31,2,1,""]},"utilities.decorators":{brand_console:[32,6,1,""],registered_user_only:[32,6,1,""],staff_user_only:[32,6,1,""]},"utilities.theme":{ColorUtils:[34,2,1,""],UiTheme:[34,2,1,""],render_skin:[34,6,1,""]},"utilities.theme.ColorUtils":{cvt_hex_rgb:[34,4,1,""],cvt_rgb_hex:[34,4,1,""],scale_hex_color:[34,4,1,""],scale_rgb_color:[34,4,1,""]},"utilities.validators":{validate_hex_color:[35,6,1,""]},"watchdog.middleware":{ErrorLogMiddleware:[37,2,1,""]},"watchdog.models":{ErrorLog:[38,2,1,""],ReportedProblem:[38,2,1,""],Suggestion:[38,2,1,""]},"watchdog.models.ErrorLog":{clean:[38,3,1,""],construct_checksum:[38,4,1,""],post_save:[38,5,1,""],save:[38,3,1,""]},"watchdog.models.ReportedProblem":{clean:[38,3,1,""],post_save:[38,5,1,""],save:[38,3,1,""]},"watchdog.models.Suggestion":{clean:[38,3,1,""],post_save:[38,5,1,""],save:[38,3,1,""]},accounts:{exceptions:[1,0,0,"-"],forms:[2,0,0,"-"],models:[8,0,0,"-"],utils:[9,0,0,"-"],views:[10,0,0,"-"]},brands:{api:[11,0,0,"-"],forms:[12,0,0,"-"],models:[14,0,0,"-"],operations:[15,0,0,"-"]},console:{context_processors:[16,0,0,"-"],middleware:[18,0,0,"-"],views:[19,0,0,"-"]},feedvay:{views:[22,0,0,"-"]},owlery:{models:[27,0,0,"-"],owls:[28,0,0,"-"]},utilities:{api_utils:[29,0,0,"-"],aws:[30,0,0,"-"],custom_storages:[31,0,0,"-"],decorators:[32,0,0,"-"],theme:[34,0,0,"-"],validators:[35,0,0,"-"]},watchdog:{middleware:[37,0,0,"-"],models:[38,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","exception","Python exception"],"2":["py","class","Python class"],"3":["py","method","Python method"],"4":["py","staticmethod","Python static method"],"5":["py","classmethod","Python class method"],"6":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:exception","2":"py:class","3":"py:method","4":"py:staticmethod","5":"py:classmethod","6":"py:function"},terms:{"case":[4,6,8,10,13,14,17,27,32,38],"class":[1,2,8,9,11,12,14,18,23,24,27,28,29,31,34,37,38],"default":[6,8,17,21],"enum":14,"function":[3,8,21,32],"import":6,"int":29,"new":[2,4,8,9],"null":38,"public":[6,7,8,11,14,38],"return":[2,8,10,11,13,14,15,16,21,27,28,29,30,32,34,35],"static":[8,14,21,22,28,34,38],"super":14,"switch":17,"throw":[8,14,34],"true":[2,8,14,34,35],"while":[8,11,27],_obj:34,_sessionstor:6,abl:6,about:[11,13,22,27,28,36],absolut:[22,34],accept:[8,14,22],access:[6,8],accord:[10,27,28],accordingli:[22,27],account:[1,2],accounts_clear_user_token:23,acl:31,across:[8,17,25,33],act:27,action:[8,13,25,27],activ:[8,14],active:9,actual:[6,8,22,27,28],add:[8,14,29],add_own:14,add_update_attribut:8,adding:8,addit:8,address:28,admin:[6,7,32],administr:6,advantag:8,after:[2,4,6,8,10,32,38],again:[8,14],against:18,aggreg:8,all:[2,3,6,8,10,11,13,14,15,16,17,18,19,21,23,24,25,26,27,28,36,38],alloc:8,allow:[4,9,17,32],along:[2,4,8,28,38],alreadi:[8,9,14,17],also:[8,14,21,36],alwai:[8,27,29,38],amazon:[30,31],analysi:17,analyz:17,ani:[6,8,9,11,14,17,21,28,32,36],any:[8,26,28],anyon:26,api:10,api_nam:11,api_util:[10,29],apirespons:[10,29],applic:[11,15,21,36],appropri:13,area:[36,38],arg:[8,14,22,27,38],ask:2,assign:17,associ:[13,14,17,28],asynchron:28,atom:14,attribut:8,attribute_nam:8,audit:[8,14],auth:8,authent:[14,17,32],author:[1,2,8,9,10,11,13,14,15,16,18,22,23,24,27,28,29,31,32,34,35,37,38],auto_id:[2,12],auto_sav:[8,14],automat:[4,6,8,21,27,30,36],avail:[8,9],aws:[0,31],awya:14,back:[6,8,22],backend:13,bar:21,base:[8,21,38],basi:[9,27],basic:[2,8,21],basicinfoform:2,batch:27,becaus:[6,8],been:[2,8,13,14,15,18,21,27,36,38],befor:[8,10,17],begin:17,behavior:17,belong:26,below:14,beta:36,beyond:6,birth:2,block:22,bodi:27,bool:[8,14,34,35],bootstrap:21,both:[14,17],brand:8,brand_consol:32,brand_set:14,brand_uid:[17,18],brandchangereq:28,brandchangerequest:[13,14,28],brandchangerequestapi:11,brandcreateeditform:[12,14],brandexistenceapi:11,brandowner:[13,14],broad:14,broadcast:27,browser:[6,8],bucket:31,buffer:27,busi:[8,14],button:21,bypass:[17,18],cach:22,call:[8,10,17,18,21,28,38],can:[2,6,8,10,13,14,15,17,21,25,27,28,33,38],cannot:[8,14,22],captur:[8,14,37,38],care:[13,14,17,36],cater:29,caution:14,certain:9,ch_purpose:8,challeng:26,chang:[2,8,21,29],change_statu:29,charact:35,chart:[8,14],check:[4,9,10,14,17,18,27,32],checksum:38,claim:[8,14,15],claim_reg_us:15,class_nam:38,classif:[4,9],classifi:9,classifyregisteredus:9,classmethod:[8,38],clean:[8,14,27,38],clear:[],click:4,client:[6,14],close:[6,10,30],clr_prim_dis:34,clr_prim_hov:34,clr_primari:34,code:[2,4,8,10,27,28,29,34,35],collabor:[0,17],color:[14,21,34,35],colorutil:34,com:[6,22],come:27,command:21,common:[14,17],commun:28,compani:14,complet:[5,7,10,13,28],complete_sav:8,complex:8,compon:[21,34],compos:28,concaten:8,concept:26,conf:6,configur:[6,20,22],confirm:[8,13,28],confus:17,connect:27,consid:17,consist:13,consol:16,consolebrandswitchmiddlewar:[17,18],constraint:14,construct:38,construct_checksum:38,construct_usernam:8,consum:[22,27],contain:[6,8,10,28],content:[],content_typ:30,context:[],context_processor:16,continu:13,contract:14,contrib:[6,8],convert:[28,34],cooki:[6,8],correct:13,correspond:[18,26],could:17,countri:8,country_tel_cod:8,cpu:22,creat:[6,8,12,17,18,21,22,24,29,38],create_brand_change_log:15,create_edit_brand:14,create_new_brand:15,created_on:27,creation:4,criteria:27,cron:[25,27,28],cross:8,css:[21,22,24,34],curr_brand:[17,18],current:[8,17,21,36],custom:[],custom_storag:31,cvt_hex_rgb:34,cvt_rgb_hex:34,dai:27,darker:[21,34],dashboard:17,data:[2,8,12,14,15,27,29,35,38],databas:[6,8,14,17,18,26,27,28,37,38],date:[2,8,27],datetim:[2,27],decor:[],defin:[13,14,17,18,21,27,28,34],delet:[8,10,11,14,23],delete_attribut:8,delete_own:14,deliv:26,deliveri:26,deni:9,depend:6,depict:26,describ:[5,7,9],descript:13,design:17,desktop:21,detail:[2,8,9,10,13,14,15],detailedattribut:8,determin:[6,27],devic:[21,27,28],diagram:[5,7,8,14],dict:[2,8],dictionari:[8,15],differ:[6,17],digit:[8,27],dimens:14,direct:[8,10],directli:[8,10,14],directori:[21,24],disabl:[8,14,21,34],disassoci:[],discuss:[6,13],dispatch:[17,27,28],displai:8,divid:4,django:[2,6,7,8,12,16,17,20,21,22,23,24,25,29,32],djangoproject:6,dob:2,doc:[6,22],doe:[6,8,21,22,27,30,32],does_exist:14,doesnotexist:14,domain:17,done:[8,14,22],dsiplai:27,dure:[8,10,38],each:[8,13,21,26,28],earlier:4,eas:17,easili:[8,17],edg:14,edit:21,either:4,els:[2,8,10,14,27,28,34],email:[4,8,10,14,26,27,28,38],email_address:28,emailmessag:[27,28],emailowl:28,embed:8,empty_permit:[2,12],enabl:37,encapsul:15,encount:[1,22],engin:6,enough:2,enter:[4,9,10],enterpris:8,entir:[14,15,17,21],entiti:[8,14,28],entri:[8,13,14,17,27,28],entry:14,environ:25,error:[2,8,15,17,28,34,36,37,38],error_class:[2,12],error_log:38,errorlist:[2,12],errorlog:38,errorlogmiddlewar:[37,38],etc:[3,8,9,13,14,15,17,20,21,22,27,28,31,36],evalu:13,even:18,everi:[6,8,27,28],everyth:[8,14],exampl:[6,8,18,28],exce:6,except:[1,8,14,18,28,37],exception:[],exclud:11,execut:[8,13,27],exist:[8,11,14],expir:[6,10,23],explain:6,explicitli:[6,27],extend:6,extract:17,fact:18,fail:[8,14],failur:[13,15,28,32],fals:[2,8,12,14,15,23,24,34],famou:26,featur:21,feedback:[0,17,36],feedvay_update_theme_skin:[21,24],feel:[21,38],fetch:[17,22],field:[8,14,15,27,38],field_ord:[2,12],file:[2,12,14,15,21,22,24,30,31,34],file_icon:15,file_log:15,file_obj:30,filenam:30,files:15,fill:[13,15,21,27],find:8,finish:10,fire:8,firm:14,first:[10,18,38],first_nam:8,flow:[3,4,7,8,10,13],flowchart:[5,7],follow:[5,6,7,8,9,13,14,21,26,28,29,35],force_logout_us:8,force_send:27,forcefulli:[8,27],foreign:6,forgot:10,form:[],format:[8,14],found:[8,14],freez:14,from:[2,4,6,7,8,13,14,17,18,22,23,24,26,27,28,29,38],further:[8,17],futur:26,gagandeep:[1,2,8,9,10,11,14,15,16,18,22,23,24,27,28,29,31,32,34,35,37,38],gap:6,gen_http_respons:29,gender:2,gener:[14,21,29,32],generate_uithem:14,genuin:8,get:[8,10,11,22],get_date_of_birth:2,get_meta_dict:8,get_or_cr:27,get_respons:[18,37],give:[6,13,14,21],given:[8,9,10,11,13,14,28,34],goe:13,good:8,grab:36,group:[14,27],guess:30,guidelin:[6,28],had:28,handl:[10,14,15,18,19,22,26,28,29,36],handler:[8,28],handov:26,hard:17,harri:26,have:[8,13,14,15,17,22,25,27,36],header:22,health:36,heavi:[13,15],henc:[6,8],here:[6,8,13,17],hex:[14,34,35],hex_color:34,hierarchi:14,him:27,himself:[8,10,14],hit:17,hour:6,hover:[21,34],howev:[6,8,13,14,17,27,38],html:[14,22],http:[6,22,29,32],human:17,icon:[14,15],id_:[2,12],identifi:17,ignor:8,imag:14,imagefieldfil:14,img_obj:14,immedi:[13,28],implement:[15,17],import_modul:6,importlib:6,improv:[36,38],inact:[8,14],inactiv:9,incas:[6,8],incase:38,includ:[2,8,14,20,27,30,36,38],incomplet:9,incorrect:14,increas:6,independ:[27,28],index:[0,8],individu:[17,27],inform:[2,6,8,11,13,14,15,17,18,22,27],infrastructur:17,inherit:38,initi:[2,12],inmemori:14,inmemoryuploadedfil:14,inord:6,inplac:[13,15],inplace:13,insecur:22,insid:[6,8,11,18,25],inside:28,inspinia:[21,24,34],inspir:26,instanc:[2,6,8,13,14,17,27,28,29,38],instead:[6,17],integrityerror:14,intellig:0,intend:26,interv:27,intervent:8,introduc:17,invalid:[1,14,34],invalidregisteredus:[1,8],irrespect:14,irrevers:13,is_new:8,is_valid:15,issu:8,itself:13,json:[10,14,27,29,34],jsonrespons:29,justifi:6,keep:[6,8,36],kei:[6,8,29],kept:[8,26],kickstart:2,kind:[16,21,27,28],king:35,know:27,known:[8,14],kwarg:[8,14,22,27,29,34,38],label_suffix:[2,12],land:17,last:8,last_nam:8,last_reg_d:10,last_updated_on:8,later:21,lead:[8,9,17],left:28,length:22,level:24,licens:21,like:27,limit:[10,11],link:[8,10,30,36,38],list:[2,6,8,11,14,23,24,27,28,34,38],list_attribut:8,load:22,local:6,lock:8,lock_attribut:8,log:[2,4,6,8,10,14,15,16,17,22,25,26,32,36,37,38],login:[2,3,6],login_url:32,logo:[13,14,15],logo_dim:14,logo_max_size:14,logout:[8,10],longer:13,look:21,lookup:8,loop:8,made:[6,8,13,14,36,38],mai:[17,27,28,38],mail:8,main:17,maintain:[6,8,17,26,27,36],mainten:36,major:6,make:[8,13,14,17,21,22,38],manag:3,mandatori:[8,14],mang:13,mani:21,manipul:34,manner:28,manual:[8,13,21],map:[6,8],mark:[8,14,27],mark_send:27,market:0,match:[10,18],maximum:11,mean:[13,14,28],meant:[7,11,17,27],mechan:[],media:31,mediastorag:31,memori:22,messag:[1,13,26,27,28,29,38],messi:17,meta:8,method:[2,6,8,14,15,27,28,29,30,34,35,38],middlewar:17,midllewar:17,might:[6,8],migrat:[13,14],mind:6,minor:21,mobil:[4,8,10,21,27,28],mobile_no:[8,28],modal:14,mode:8,model:[2,3,6],mongodb:[8,14,27,38],more:[2,6,14],moreov:17,mostli:[4,6,8,11,25,28,29],mous:[21,34],multicast:27,multipl:[8,14],must:[8,9,14,15,21,26,27,28,30,32,36,38],mysql:[8,14,27,38],name:[2,8,13,14,27,36,38],nav:21,necessari:[8,13],need:[14,15],neg:34,nest:8,never:[6,8,21,27],new_password:8,next:32,nginx:22,nice:21,no_color:[23,24],none:[2,8,11,12,15,18,23,24,27,28,30,31,34,37,38],normal:[10,18],note:8,noth:2,notif:[14,27,28],notif_expiry:27,notificationmessag:[27,28],notificationowl:28,notificationrecipi:27,now:[2,8,10,14,27],number:[2,4,8,10,27,28,36],object:[2,8,14,30],obtain:[4,6,27],occur:[28,36,37,38],off:18,offer:[17,21],old:8,once:[13,14],one:8,onli:[6,7,8,10,11,14,15,22,27,32,38],only:[4,8,10,11,14,38],open:[10,17,36],oper:[13,14,15,17],operat:[],optim:8,option:[6,13],optional:[15,28],organis:8,other:[6,8,14,17],otherwis:[10,32,38],over:[8,13,26,36],overcom:17,overrid:[8,9],overridden:8,owl:8,owleri:[],own:[17,21],owner:[13,14,21,28],ownership:[13,14],page:[0,2,4,18,28,32],pair:[6,8,15,29],param:14,paramet:[2,8,9,14,15,21,24,27,28,30,34,35],paramt:24,parent:38,partial:14,partner:28,pass:[8,30],passiv:8,password:[2,3],passwordchangeform:2,passwordresetform:2,path:[17,18,22,30],path_info:18,pend:[9,13,15,27],peopl:14,per:[6,8,18,21,28],perform:[8,22,25],perhap:17,period:[27,28],permiss:[8,14,17],person:8,phone:[2,8],pick:[27,28],place:[21,26],placehold:21,plant:17,platform:[0,17,27,36],pleas:[8,17,22],pobs:[8,13,14,17],point:[8,11,14,15,27,28,38],popul:8,portal:[6,21],posit:34,possibl:[8,27],post:[8,10,38],post_sav:[8,38],potter:26,pre:[8,14,27,38],predefin:26,prefix:[2,8,12,18],present:[8,9,27,28,38],prevent:[8,22],previou:13,primari:[14,21,34],primary_color:14,primary_dark:21,primary_dis:21,prioriti:28,privat:2,privateinfoform:2,problem:[17,36,38],procedur:15,process:[4,5,8,10,22,25,26,27,28],processor:[],profil:2,project:[6,17,20],prone:17,properti:14,provid:[4,6,8,13,14,15,17,22,33,36,38],provis:[13,17],publish:17,pull:27,purchas:21,purpos:[8,17],push:[27,28],python:[21,23,24,33],queri:[6,8,11,27],queu:14,queue:27,quick:8,rais:[8,27],rang:35,rather:[21,22,27,38],read:[8,21,24,27],real:13,reason:[8,13,14],receiv:[6,8,13,26,27,28],recipi:27,recommend:8,record:[8,11,13,14,27,38],recov:2,recover_account:10,recoveri:3,redi:6,redirect:[4,10,28,32],redirect_field_nam:32,reduc:8,redund:17,refer:[6,8,17,22,26,38],reflect:14,reg_us:[14,15],reg_user_disass:28,regex:18,regist:[1,2,4,7,8,9,10,16,17,32],registered_user_onli:32,registeredus:[1,8,9,10,14],registerus:8,registr:[2,3,4],registration_clos:10,registration_open:10,registration_resend_cod:10,registration_verifi:10,registrationform:2,reject:[8,38],relas:13,relat:[3,8,13,15,17,32],releas:[8,13],reli:28,remain:[8,14],remark:[8,9,21,38],rememb:6,remov:[8,13,14,17,27],render:[21,34],render_skin:34,render_them:21,replac:8,report:[8,36,38],reportedproblem:38,repres:8,request:[6,8,10,11,13,14,15,16,17,18,19,22,27,28,29,37],requir:[8,16,27,28,36],reregister_or_update_brand:15,reset:[2,3,4,10,28],reset_password_plea:10,reset_password_plea_verifi:10,resolv:[6,8,17],resourc:[],respect:24,respons:[3,10,21,22,26,28,29,36],restrict:14,result:27,retriev:[6,18],reusabl:33,review:[13,14],revis:[14,15],reviv:8,rgb:34,right:14,role:14,root:20,rout:[],routin:[26,33],run:[17,28],runtim:[27,36,37,38],same:[4,6,8,17,18,26],save:[2,8,14,27,38],scale:34,scale_hex_color:34,scale_rgb_color:34,schema:6,school:26,score:8,screen:7,search:[0,11],second:6,section:[6,13,25],secur:8,see:[],seed:21,seem:17,seen:36,select:6,self:13,send:[2,4,6,8,10,13,14,22,26,27,28],send_brand_change_request:28,send_brand_disassociation_success:28,send_brand_partner_left_messag:28,send_brand_partner_left_notif:28,send_owl:[8,14],send_password_change_success:28,send_password_reset:28,send_reg_verif:28,sender:[8,38],sendfil:22,separ:[6,13,14],seper:27,sequenti:13,seri:26,serv:22,server:[8,22,36],servic:[14,17,27,28,30,31],session:3,session_cookie_age:6,session_cookie_age_public:6,session_engine:6,session_id:8,session_kei:6,sessionstor:[6,8],sessionstro:6,set:[2,4,6,8,10,13,14,17,18,20,21,24,25,27,28,29,31,37],set_password:8,shift:6,should:[6,17],shown:[14,27],side:14,sign:10,signal:8,signatur:21,signifi:14,silent:[8,17],simpl:17,simplest:17,simpli:[8,14,18,22],sinc:[4,8,14,21],singh:[1,2,8,9,10,11,14,15,16,18,22,23,24,27,28,29,31,32,34,35,37,38],singl:27,situat:9,six:35,size:14,skin:[],slug:14,small:[13,17,21],sms:[4,8,10,14,26,27,28],smsmessag:[27,28],smsowl:28,some:[21,27,28],sourc:36,specif:[21,27],specifi:[13,27],sphinx:22,staff:[6,7,8,9,13,14,22,32,36],staff_user_onli:32,stage:27,start:35,state:[8,9,13,14],statechart:8,statu:[2,8,9,10,11,13,14,15,27,29,36],stderr:[23,24],stdout:[23,24],still:15,stop:14,storag:6,store:[6,8,13,14,21,27,28,38],stream:22,string:[27,34,35],strip:18,structur:21,student:26,style:[21,24,34],submit:13,success:[8,28],successfulli:[8,14],suggest:[36,38],superus:32,sure:22,survei:[0,17],suspend:9,suspended:9,system:[7,25,27,36,38],tag:8,take:[8,13,14,24,27,36],taken:17,target:27,task:13,tastypi:11,team:17,technic:[8,22],telephon:8,tell:10,templat:[14,17,21,24,26,28,34],term:[14,21,36],text:[11,21,38],than:[2,6],thei:[8,14,17,27,28],them:[8,14,17,27,28,36],theme:20,theme_default:[21,24],thi:[2,5,6,7,8,9,10,11,13,14,15,17,18,21,22,24,25,26,27,28,29,30,32,34,36,38],thier:36,those:[28,38],thread:22,thrown:28,time:[2,6,8,14,27,36],timezon:2,toggl:14,token:[3,8,10],tool:[9,33],top:14,topic:6,traceback:[36,38],traceback_text:38,track:[8,27,36],tradit:8,trail:[8,14],trans_approv:8,trans_delet:14,trans_disapprov:8,trans_regist:8,trans_revise_verif:14,trans_verifi:14,trans_verification_complet:8,trans_verification_fail:14,transit:[8,13,14],transmiss:27,transpar:[21,34],tri:[10,30],trigger:[8,38],truncat:8,truth:8,tupl:[2,8],turn:22,two:[4,6,8,17],type:[6,10,11,14,22,27,30,36],typic:13,ui_them:14,uid:17,uithem:[14,34],unabl:10,unawar:2,under:14,unicast:27,uniqu:[8,14],unlock:8,unlock_attribut:8,unnecessari:22,unsent:27,until:8,unusu:17,unverifi:[4,10,14],unverified:9,unwind:8,updat:[2,8,13,14,15,21,24,27,29,38],update:[],update_session_auth_hash:8,update_them:14,update_theme_fil:14,upload:30,upload_to_s3:30,upon:6,url:10,usag:32,use:[8,14],use_required_attribut:[2,12],used:21,user:[1,2,3,4],user_id:8,user_logged_in_handl:8,user_logged_out_handl:8,user_token:28,userattribut:8,userclaim:8,usernam:[2,4,8,9,28],userprofil:[2,8],usersess:[6,8],usertoken:[8,23,28],usual:21,usualli:15,util:[2,9],utiliti:3,utilti:10,valid:[8,9,10],validate_hex_color:35,validate_icon_imag:14,validate_logo_imag:14,validate_sms_no:27,validationerror:[8,27],valu:[8,14,15,27,29,34,35],variabl:[16,18],variat:21,varieti:8,variou:[5,7,8,13,14,17,28,33,35,38],verif:[2,4,9,10,13,14,15,28],verifi:[4,8,9,10,13,14,15,32],verification_pend:[8,10,13],verified:9,verify_user_token:8,version:21,via:[6,10],view:[3,6],viw:28,wai:[5,6,7,8,17,18],wait:13,want:[14,17,26],watch:36,watchdog:[],watchdog_errorlog_enabled:37,websit:8,well:[8,10,14,17,18,21,24,36],were:2,when:[1,6,8,10,13,14,17,22],whenev:8,where:[4,8,9,17,26,27,28,30],wherea:8,which:[2,6,8,13,17,18,21,22,26,27,28,34],who:[10,26,27,28],whom:28,why:14,wide:8,wish:26,within:13,without:[2,8,15,17,25],work:[6,13,17],workflow:28,world:13,would:17,wrapper:[14,34],write:8,wsgi:20,you:[6,8,14,22,28],your:[8,28],zacharyvoas:22},titles:["Welcome to feedvay&#8217;s documentation!","Exceptions","Forms","Accounts","Password Recovery","User Registration","Session Management","User Login","Models","Utilities","Views","Resource API","Forms","Brands","Models","Operations","Context Processors","Console","Middleware","Views","Main App","Project Theme","Views","Accounts Management Commands","Main Management Commands","Management Commands","Owlery","Models","Owls","Api utilities","AWS","Custom Storages","Decorators","Utilities","Theme","Validators","Watchdog","Middleware","Models"],titleterms:{"new":13,account:[3,4,23],after:13,api:[11,29],app:[0,20],aws:30,brand:[13,17],chang:13,clear:23,command:[23,24,25],consol:17,content:[3,13,17,20,26,33,36],context:16,creat:13,creation:[],custom:[21,31],decor:32,disassoci:13,document:0,edit:13,exception:1,expiri:6,extension:6,featur:36,feedvai:0,form:[2,12],framework:6,indice:0,login:7,main:[20,24],manag:[6,23,24,25],mechan:17,middlewar:[18,37],model:[8,14,27,38],modul:[0,3,20],operat:[13,15],owl:28,owleri:26,password:4,plea:4,processor:16,project:21,recov:4,recoveri:4,regist:13,registr:5,reject:13,resourc:11,rout:17,session:6,skin:[21,24],storag:31,tabl:0,theme:[21,24,34],through:[5,7],token:23,update:24,url:17,user:[5,7,17,23],util:29,utiliti:[9,33],valid:35,view:[10,19,22],watchdog:36,web:[5,7],welcom:0}})