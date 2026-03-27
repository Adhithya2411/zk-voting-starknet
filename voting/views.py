from django.http import JsonResponse

def generate_proof(request):
    # TODO: We will import PoseidonMerkleTree here next!
    return JsonResponse({"status": "success", "message": "Django is alive and ready for ZK Math!"})