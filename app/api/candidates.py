from flask import jsonify, request
from flask_restful import Resource
from app.main import db
from app.models.candidate import CandidateProfile
from app.api import bp

class CandidateAPI(Resource):
    def get(self, candidate_id=None):
        if candidate_id:
            candidate = CandidateProfile.query.get_or_404(candidate_id)
            return jsonify(candidate.to_dict())
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        candidates = CandidateProfile.query.paginate(page=page, per_page=per_page)
        return jsonify({
            'items': [item.to_dict() for item in candidates.items],
            'meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': candidates.pages,
                'total_items': candidates.total
            }
        })

bp.add_resource(CandidateAPI, '/candidates', '/candidates/<int:candidate_id>')