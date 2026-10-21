/* Verification-only synchronous compatibility driver. The production flow
 * engine remains callback-free. This driver lets the existing synchronous
 * controls harness compare all old inputs; it is not a live scheduler. */
#include "biwn_coordinate_services.h"
static uint64_t contexts,requests,external_requests,completed_calls;
int biwn_coordinate_flow_drive_for_check(struct biwn_world_bus *bus,
 biwn_coordinate_write8 byte_write,uint32_t budget,uint32_t incoming,uint32_t *out)
{
 struct biwn_coordinate_flow state;
 struct biwn_coordinate_request request;
 struct biwn_coordinate_completion reply;
 uint32_t result;int status,service;
 if(!bus||!byte_write||!out||!budget)return BIWN_COORDINATE_BAD_ARGUMENT;
 if(contexts==UINT64_MAX)return BIWN_COORDINATE_LIMIT;
 status=biwn_coordinate_flow_begin(&state,++contexts,incoming);
 if(status)return BIWN_COORDINATE_BAD_ARGUMENT;
 status=biwn_coordinate_flow_advance(&state,0,&request);
 while(status==BIWN_COORDINATE_FLOW_REQUEST){
  if(!budget--)return BIWN_COORDINATE_LIMIT;
  requests++;result=request.incoming_d0;
  service=biwn_coordinate_service_request(bus,byte_write,&request,&result);
  if(service==BIWN_COORDINATE_SERVICE_EXTERNAL){
   external_requests++;
   if(bus->call(bus->context,request.address,request.argument_count?&request.argument:0,request.argument_count,&result))
    return BIWN_COORDINATE_DEPENDENCY_ERROR;
  }else if(service!=BIWN_COORDINATE_SERVICE_COMPLETED)
   return service==BIWN_COORDINATE_SERVICE_BUS_ERROR?BIWN_COORDINATE_BUS_ERROR:BIWN_COORDINATE_DEPENDENCY_ERROR;
  reply=(struct biwn_coordinate_completion){request.context,request.sequence,result,0};
  status=biwn_coordinate_flow_advance(&state,&reply,&request);
 }
 if(status!=BIWN_COORDINATE_FLOW_DONE)return BIWN_COORDINATE_DEPENDENCY_ERROR;
 if(biwn_coordinate_flow_result(&state,out)!=BIWN_COORDINATE_FLOW_DONE)return BIWN_COORDINATE_DEPENDENCY_ERROR;
 completed_calls++;return 0;
}
uint64_t biwn_coordinate_flow_check_stat(uint32_t index)
{
 switch(index){case 0:return contexts;case 1:return requests;case 2:return external_requests;
 case 3:return completed_calls;default:return 0;}
}
